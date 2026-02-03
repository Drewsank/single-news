"""Создание базы данных Источники в Notion"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

# RSS источники по категориям
RSS_SOURCES = [
    # RWA / Токенизация
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "verticals": ["RWA", "DeFi"]},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed", "verticals": ["RWA", "DeFi"]},
    {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "verticals": ["RWA", "DeFi"]},
    {"name": "Blockworks", "url": "https://blockworks.co/feed/", "verticals": ["RWA", "DeFi"]},

    # Agriculture
    {"name": "The Astana Times", "url": "https://astanatimes.com/feed/", "verticals": ["Agriculture"]},
    {"name": "World Grain", "url": "https://www.world-grain.com/rss", "verticals": ["Agriculture"]},
    {"name": "Romania Insider", "url": "https://www.romania-insider.com/feed", "verticals": ["Agriculture"]},
    {"name": "Grain Central", "url": "https://www.graincentral.com/feed/", "verticals": ["Agriculture"]},

    # Mainstream
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/", "verticals": ["Mainstream"]},
    {"name": "TechCrunch Crypto", "url": "https://techcrunch.com/category/cryptocurrency/feed/", "verticals": ["RWA", "DeFi", "Mainstream"]},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "verticals": ["RWA", "DeFi", "Mainstream"]},
]

def main():
    api_key = os.getenv("NOTION_API_KEY")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    # Находим родительскую страницу (News for Clients)
    parent_page_id = "2f77eb3f-b6bb-8055-9010-d60da4127656"

    print("=== Создание базы данных 'Источники' ===\n")

    try:
        # Создаем базу данных
        new_db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "Источники RSS"}}],
            properties={
                "Название": {"title": {}},
                "RSS URL": {"url": {}},
                "Вертикаль": {
                    "multi_select": {
                        "options": [
                            {"name": "RWA", "color": "green"},
                            {"name": "Agriculture", "color": "blue"},
                            {"name": "DeFi", "color": "purple"},
                            {"name": "Mainstream", "color": "orange"},
                        ]
                    }
                },
                "Активен": {"checkbox": {}},
            }
        )

        db_id = new_db["id"]
        print(f"База создана! ID: {db_id}")
        print(f"URL: {new_db['url']}")

        # Сохраняем ID в .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            content = f.read()
        content = content.replace("NOTION_SOURCES_DB_ID=", f"NOTION_SOURCES_DB_ID={db_id.replace('-', '')}")
        with open(env_path, "w") as f:
            f.write(content)
        print(f"\nID сохранен в .env")

        # Добавляем источники
        print(f"\n=== Добавление {len(RSS_SOURCES)} источников ===\n")

        for source in RSS_SOURCES:
            page = notion.pages.create(
                parent={"database_id": db_id},
                properties={
                    "Название": {"title": [{"text": {"content": source["name"]}}]},
                    "RSS URL": {"url": source["url"]},
                    "Вертикаль": {"multi_select": [{"name": v} for v in source["verticals"]]},
                    "Активен": {"checkbox": True},
                }
            )
            print(f"  + {source['name']} ({', '.join(source['verticals'])})")

        print(f"\n Готово! Добавлено {len(RSS_SOURCES)} источников.")

    except Exception as e:
        import traceback
        print(f"Ошибка: {e}")
        traceback.print_exc()
    finally:
        http_client.close()

if __name__ == "__main__":
    main()
