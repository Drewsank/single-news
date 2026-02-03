"""Проверка структуры базы Источники"""
import os
import json
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print(f"Database ID: {db_id}\n")

    try:
        db = notion.databases.retrieve(db_id)
        print("=== Полная структура базы ===")
        print(json.dumps(db, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    main()
