#!/usr/bin/env python3
"""Submit the Golden Demo report using the JWT token."""
import asyncio
import json
import sys
import os
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.auth.jwt import create_access_token
from app.db.session import AsyncSessionLocal
from app.db.models import User
from sqlalchemy import select


async def main():
    email = "demo@factanchor.test"
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            print("ERROR: Test user not found")
            sys.exit(1)

    token = create_access_token(str(user.id))

    # Report text from demo/sample_report.txt (inline — demo/ not mounted in container)
    report_text = (
        "Meridian Corp: Q3 2025 Performance Review\n\n"
        "The third quarter of 2025 proved to be highly lucrative for Meridian Corp. "
        "Despite localized strikes in its South American delivery hubs during early 2025 "
        "and regulatory headwinds in the European Union that delayed the launch of the "
        "predictive forecasting module by six months, the company rebounded significantly. "
        "The release of the new CyberShield product line represented the largest product "
        "launch in Meridian Corp's history, propelling Q3 2025 revenue to a staggering $4.5B. "
        "This contributed to Net Income jumping to $950M, while the Operating Margin rested "
        "comfortably at 22.5%. Further fueling their competitive edge, the company successfully "
        "acquired AlphaLogistics in Q2 2025 to bolster its supply chain capabilities, "
        "reinforcing their market position.\n\n"
        "Internally, Meridian Corp has executed bold operational shifts. The board of directors "
        "appointed Sarah Jenkins as the new Chief Technology Officer in late 2024, ushering in "
        "an era of rapid modernization. By Q3 2025, Headcount expanded to 14,500 employees. "
        "To maintain an agile workforce, the company implemented a hybrid 3-day work-from-office "
        "policy globally in 2025. Financial health remains absolute, with the company commanding "
        "a massive Cash Balance of $8.2B by the end of the quarter. Commitment to future "
        "innovation was underscored by an aggressive R&D Spend of $675M.\n"
    )

    # Submit to API
    url = "http://localhost:8000/api/v1/reports"
    payload = json.dumps({"text": report_text, "title": "Meridian Corp Q3 2025"}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            print(f"STATUS={resp.status}")
            print(f"REPORT_ID={body.get('report_id')}")
            print(f"TOTAL_CLAIMS={body.get('total_claims')}")
            print(f"WS_URL={body.get('ws_url')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR={e.code} {body}")


if __name__ == "__main__":
    asyncio.run(main())
