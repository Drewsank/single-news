"""Debug Notion database"""
import os
import json
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

api_key = os.getenv("NOTION_API_KEY")
db_id = "2f77eb3fb6bb80808c76e64eec0b7523"

http_client = httpx.Client(timeout=60.0)
notion = Client(auth=api_key, client=http_client)

print("Fetching database...")
db = notion.databases.retrieve(db_id)

print("\n=== FULL DATABASE RESPONSE ===")
print(json.dumps(db, indent=2, ensure_ascii=False))

http_client.close()
