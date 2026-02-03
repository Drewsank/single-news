"""Обновление базы Источники - добавление свойств"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print(f"=== Обновление базы Источники ===")
    print(f"Database ID: {db_id}\n")

    try:
        # Обновляем базу, добавляя свойства
        updated_db = notion.databases.update(
            database_id=db_id,
            properties={
                "Name": {"title": {}},
                "RSS URL": {"url": {}},
                "Vertical": {
                    "multi_select": {
                        "options": [
                            {"name": "RWA", "color": "green"},
                            {"name": "Agriculture", "color": "blue"},
                            {"name": "DeFi", "color": "purple"},
                            {"name": "Mainstream", "color": "orange"},
                        ]
                    }
                },
                "Active": {"checkbox": {}},
            }
        )

        print("База обновлена!")
        print("\nСвойства:")
        for name, prop in updated_db.get("properties", {}).items():
            print(f"  - {name} ({prop['type']})")

    except Exception as e:
        import traceback
        print(f"Ошибка: {e}")
        traceback.print_exc()
    finally:
        http_client.close()

if __name__ == "__main__":
    main()
