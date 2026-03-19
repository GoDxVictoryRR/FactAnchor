import uuid
import json
from celery.utils.log import get_task_logger
from .celery_app import app
from ..verification.sql_verifier import verify_sql_claim
from ..verification.vector_verifier import verify_vector_claim
from ..verification.confidence import generate_confidence_score
from ..db.session import SyncSessionLocal
from ..db.models import Report, Claim
from sqlalchemy import select, update
import redis
from ..config import settings

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

logger = get_task_logger(__name__)

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    queue="verification",
    time_limit=30,
    soft_time_limit=25
)
def verify_claim(self, claim_id: str, report_id: str):
    """
    Task to verify a single claim using either SQL or Vector strategy.
    """
    logger.info(f"TASK START: verify_claim {claim_id} for report {report_id}")
    try:
        session = SyncSessionLocal()
        try:
            # Fetch all claims for this report
            rid = uuid.UUID(report_id)
            result = session.execute(
                select(Claim).where(Claim.report_id == rid)
                .order_by(Claim.sequence_num)
            )
            claims = list(result.scalars().all())
            
            logger.info(f"Found {len(claims)} claims for report {report_id}")

            for claim in claims:
                if claim.status not in ('pending', None, ''):
                    logger.info(f"Skipping claim #{claim.sequence_num} (status: {claim.status})")
                    continue

                logger.info(f"ACTUALLY VERIFYING claim #{claim.sequence_num}: {claim.claim_text[:50]}")

                entities = claim.entities or []
                if claim.claim_type == 'quantitative':
                    logger.info(f"Strategy: SQL for claim #{claim.sequence_num}")
                    vr = verify_sql_claim(claim.claim_text, entities)
                    claim.status = vr.status
                    claim.llm_generated_sql = vr.llm_generated_sql
                    claim.error_message = vr.reason
                else:
                    logger.info(f"Strategy: Vector for claim #{claim.sequence_num}")
                    try:
                        vr = verify_vector_claim(claim.claim_text)
                        claim.status = vr.status
                        claim.similarity_score = vr.similarity_score
                        claim.error_message = None
                    except Exception as e:
                        logger.warning(f"Vector failed for claim #{claim.sequence_num}: {e}. Falling back to SQL.")
                        vr = verify_sql_claim(claim.claim_text, entities)
                        claim.status = vr.status
                        claim.llm_generated_sql = vr.llm_generated_sql
                        claim.error_message = vr.reason

                    logger.info(f"Claim #{claim.sequence_num} result: {claim.status}")
                    
                    # Publish real-time update (non-fatal)
                    if redis_client:
                        try:
                            redis_client.publish(
                                f"report:{report_id}",
                                json.dumps({
                                    "type": "claim_update",
                                    "claim_id": str(claim.id),
                                    "status": claim.status,
                                    "sequence_num": claim.sequence_num
                                })
                            )
                        except Exception:
                            pass

            session.commit()
            logger.info(f"Committed changes for report {report_id}")
        finally:
            session.close()

        # Trigger completion check
        check_report_complete.delay(report_id)
        return {"status": "success", "report_id": report_id}

    except Exception as exc:
        logger.error(f"CRITICAL ERROR in verify_claim {report_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

@app.task(queue="verification")
def check_report_complete(report_id: str):
    """
    Checks if all claims for a report are finished and finalizes the report.
    """
    logger.info(f"COMPLETION CHECK: report {report_id}")
    try:
        session = SyncSessionLocal()
        try:
            rid = uuid.UUID(report_id)
            terminal_states = {'verified', 'flagged', 'uncertain', 'error', 'complete'}
            result = session.execute(select(Claim).where(Claim.report_id == rid))
            all_claims = list(result.scalars().all())

            non_terminal = [c for c in all_claims if c.status not in terminal_states]
            if non_terminal:
                logger.info(f"Report {report_id}: {len(non_terminal)} claims still non-terminal")
                return

            logger.info(f"FINALIZING report {report_id}: All claims terminal")
            
            # All claims are terminal — generate confidence score
            claim_dicts = []
            verified_count = 0
            flagged_count = 0
            uncertain_count = 0
            for c in all_claims:
                claim_dicts.append({
                    'id': str(c.id),
                    'status': c.status,
                    'db_expected_value': '',
                    'similarity_score': float(c.similarity_score) if c.similarity_score else 0.0,
                })
                if c.status == 'verified': verified_count += 1
                elif c.status == 'flagged': flagged_count += 1
                elif c.status == 'uncertain': uncertain_count += 1

            confidence = generate_confidence_score(claim_dicts)

            # Update report
            session.execute(
                update(Report).where(Report.id == rid).values(
                    status="complete",
                    verified_count=verified_count,
                    flagged_count=flagged_count,
                    uncertain_count=uncertain_count,
                    confidence_score=confidence.score,
                    confidence_hash=confidence.hash,
                )
            )
            session.commit()
            
            # Publish final completion (non-fatal)
            if redis_client:
                try:
                    redis_client.publish(
                        f"report:{report_id}",
                        json.dumps({
                            "type": "report_complete",
                            "confidence_score": float(confidence.score),
                            "anchor": confidence.hash
                        })
                    )
                except Exception:
                    pass

            logger.info(f"SUCCESS: Report {report_id} finalized with score {confidence.score}")
        finally:
            session.close()
    except Exception as e:
        logger.error(f"ERROR in check_report_complete {report_id}: {e}", exc_info=True)
