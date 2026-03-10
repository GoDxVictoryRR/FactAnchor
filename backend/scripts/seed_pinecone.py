#!/usr/bin/env python3
import asyncio
import json
import os
import uuid
import sys
from dotenv import load_dotenv

# We need the openai sdk and pinecone
try:
    from openai import AsyncOpenAI
    from pinecone import Pinecone
except ImportError:
    print("Missing required libraries. Run: pip install openai pinecone-client")
    sys.exit(1)

# Ensure environment is loaded (looks dynamically in script dir, then parent)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
root_dir = os.path.dirname(parent_dir)

env_path = os.path.join(root_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Constants
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "factanchor")

if not NVIDIA_API_KEY or NVIDIA_API_KEY == "PLACEHOLDER":
    print("ERROR: NVIDIA_API_KEY is missing or PLACEHOLDER in .env")
    sys.exit(1)

if not PINECONE_API_KEY or PINECONE_API_KEY == "PLACEHOLDER":
    print("ERROR: PINECONE_API_KEY is missing or PLACEHOLDER in .env")
    sys.exit(1)

from pinecone import Pinecone, ServerlessSpec

# Initialize clients
client = AsyncOpenAI(
    base_url=LLM_BASE_URL,
    api_key=NVIDIA_API_KEY
)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
index_name = PINECONE_INDEX_NAME
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=1024,  # e5-v5 default dimension is 1024 (adjust if different)
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print("Waiting for index to be ready...")
    import time
    time.sleep(10)

index = pc.Index(index_name)

async def embed_batch(texts):
    """Embeds a batch of texts concurrently via NVIDIA NIM using asyncio."""
    # We use asyncio.gather for concurrent fast embedding calls.
    # Note: If the NVIDIA endpoint supports sending an array of texts, we could do 1 request.
    # We'll batch concurrently directly for safety and max performance.
    
    async def fetch_embedding(text):
        res = await client.embeddings.create(
            input=[text],
            model=EMBEDDING_MODEL,
            encoding_format="float",
            extra_body={"input_type": "passage"}
        )
        return res.data[0].embedding

    return await asyncio.gather(*(fetch_embedding(t) for t in texts))

async def main():
    json_path = os.path.join(script_dir, "verified_facts.json")
    if not os.path.exists(json_path):
        print(f"ERROR: {json_path} not found.")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        facts = json.load(f)

    print(f"Loaded {len(facts)} facts to embed via NVIDIA NIM ({EMBEDDING_MODEL})...")
    
    # Process in batches to not overwhelm concurrency limits
    batch_size = 10
    total_upserted = 0
    
    for i in range(0, len(facts), batch_size):
        batch_texts = facts[i:i+batch_size]
        print(f"Embedding batch {i//batch_size + 1} ({len(batch_texts)} items)...")
        
        try:
            embeddings = await embed_batch(batch_texts)
        except Exception as e:
            print(f"Error calling NVIDIA API: {e}")
            sys.exit(1)

        vectors = []
        for text, embedding_vec in zip(batch_texts, embeddings):
            # Deterministic ID based on text hash to prevent duplicates if re-run
            doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, text))
            vectors.append({
                "id": doc_id,
                "values": embedding_vec,
                "metadata": {"verified": True, "text": text}
            })
            
        print(f"Upserting {len(vectors)} vectors into Pinecone index '{PINECONE_INDEX_NAME}'...")
        index.upsert(vectors=vectors)
        total_upserted += len(vectors)
        
    print(f"\n✅ Successfully embedded and upserted {total_upserted} facts!")
    
if __name__ == "__main__":
    asyncio.run(main())
