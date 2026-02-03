"""Проверка базы и заполнение источниками"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

# Все источники
ALL_SOURCES = [
    # Крипто/RWA
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "verticals": ["RWA", "DeFi"]},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed", "verticals": ["RWA", "DeFi"]},
    {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "verticals": ["RWA", "DeFi"]},
    {"name": "Blockworks", "url": "https://blockworks.co/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "verticals": ["RWA", "DeFi", "Mainstream"]},

    # RWA специализированные
    {"name": "CryptoSlate RWA", "url": "https://cryptoslate.com/feed/?post_type=rwa", "verticals": ["RWA"]},
    {"name": "CoinDesk RWA", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tags=real-world-assets", "verticals": ["RWA"]},

    # Агро
    {"name": "Farm Progress", "url": "https://www.farmprogress.com/rss.xml", "verticals": ["Agriculture"]},
    {"name": "Time.kz", "url": "https://time.kz/rss", "verticals": ["Agriculture"]},
    {"name": "Investing.com Commodities", "url": "https://www.investing.com/rss/news_14.rss", "verticals": ["RWA", "Agriculture"]},

    # Commodities
    {"name": "Oilprice", "url": "https://oilprice.com/rss/main", "verticals": ["RWA"]},

    # Mainstream
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "verticals": ["Mainstream"]},
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/", "verticals": ["Mainstream"]},
]

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = "2f77eb3fb6bb80808c76e64eec0b7523"

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print("=" * 60)
    print("CHECK AND FILL NOTION SOURCES DATABASE")
    print("=" * 60)

    try:
        # Получаем информацию о базе
        print("\n[1] Checking database structure...")
        db = notion.databases.retrieve(db_id)

        title = db["title"][0]["plain_text"] if db.get("title") else "No title"
        print(f"    Database: {title}")

        # Проверяем свойства
        properties = db.get("properties", {})
        print(f"\n    Properties found: {len(properties)}")

        prop_map = {}  # type -> name mapping
        for name, prop in properties.items():
            print(f"      - {name} ({prop['type']})")
            prop_map[prop['type']] = name

        if not properties:
            print("\n    [!] No properties found. Checking data_sources...")
            if db.get("data_sources"):
                print("    This is a Data Source database.")
                print("    Please create a regular database in Notion UI.")
                return

        # Определяем названия полей
        title_field = prop_map.get("title", "Name")
        url_field = None
        multiselect_field = None
        checkbox_field = None

        for name, prop in properties.items():
            if prop['type'] == 'url':
                url_field = name
            elif prop['type'] == 'multi_select':
                multiselect_field = name
            elif prop['type'] == 'checkbox':
                checkbox_field = name

        print(f"\n    Field mapping:")
        print(f"      Title: {title_field}")
        print(f"      URL: {url_field}")
        print(f"      Multi-select: {multiselect_field}")
        print(f"      Checkbox: {checkbox_field}")

        if not url_field:
            print("\n    [!] No URL field found. Please add a URL property to the database.")
            return

        # Добавляем источники
        print(f"\n[2] Adding {len(ALL_SOURCES)} sources...")

        success = 0
        for source in ALL_SOURCES:
            try:
                props = {
                    title_field: {"title": [{"text": {"content": source["name"]}}]},
                }

                if url_field:
                    props[url_field] = {"url": source["url"]}

                if multiselect_field:
                    props[multiselect_field] = {"multi_select": [{"name": v} for v in source["verticals"]]}

                if checkbox_field:
                    props[checkbox_field] = {"checkbox": True}

                page = notion.pages.create(
                    parent={"database_id": db_id},
                    properties=props
                )
                print(f"    + {source['name']}")
                success += 1

            except Exception as e:
                print(f"    x {source['name']}: {e}")

        print(f"\n" + "=" * 60)
        print(f"DONE! Added {success}/{len(ALL_SOURCES)} sources")
        print("=" * 60)

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
    finally:
        http_client.close()


if __name__ == "__main__":
    main()
