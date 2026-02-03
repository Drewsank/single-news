"""Добавление источников в базу данных"""
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
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print(f"=== Проверка базы Источники ===")
    print(f"Database ID: {db_id}\n")

    try:
        # Получаем структуру базы
        db = notion.databases.retrieve(db_id)
        title = db["title"][0]["plain_text"] if db.get("title") else "Без названия"
        print(f"База: {title}")

        print(f"\nПоля базы:")
        prop_map = {}
        for name, prop in db.get("properties", {}).items():
            print(f"  - {name} ({prop['type']})")
            prop_map[prop['type']] = name

        # Находим правильные названия полей
        title_prop = None
        url_prop = None
        multiselect_prop = None
        checkbox_prop = None

        for name, prop in db.get("properties", {}).items():
            if prop['type'] == 'title':
                title_prop = name
            elif prop['type'] == 'url':
                url_prop = name
            elif prop['type'] == 'multi_select':
                multiselect_prop = name
            elif prop['type'] == 'checkbox':
                checkbox_prop = name

        print(f"\nНайденные поля:")
        print(f"  Title: {title_prop}")
        print(f"  URL: {url_prop}")
        print(f"  Multi-select: {multiselect_prop}")
        print(f"  Checkbox: {checkbox_prop}")

        # Добавляем источники
        print(f"\n=== Добавление {len(RSS_SOURCES)} источников ===\n")

        for source in RSS_SOURCES:
            properties = {
                title_prop: {"title": [{"text": {"content": source["name"]}}]},
            }
            if url_prop:
                properties[url_prop] = {"url": source["url"]}
            if multiselect_prop:
                properties[multiselect_prop] = {"multi_select": [{"name": v} for v in source["verticals"]]}
            if checkbox_prop:
                properties[checkbox_prop] = {"checkbox": True}

            page = notion.pages.create(
                parent={"database_id": db_id},
                properties=properties
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
