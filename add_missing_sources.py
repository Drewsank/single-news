"""Добавление недостающих источников из handover документа в Notion"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

# Источники из handover документа, которые отсутствуют в Notion
MISSING_SOURCES = [
    # RWA / Tokenization (Unchained already added)
    {"name": "DL News", "url": "https://www.dlnews.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "BeInCrypto", "url": "https://beincrypto.com/feed/", "verticals": ["RWA", "DeFi"]},

    # Agriculture / CIS
    {"name": "AgriCensus", "url": "https://www.agricensus.com/feed/", "verticals": ["Agriculture"]},
    {"name": "Agriculture.com", "url": "https://www.agriculture.com/feed/", "verticals": ["Agriculture"]},
    {"name": "Ag Funder News", "url": "https://agfundernews.com/feed", "verticals": ["Agriculture"]},

    # Agriculture / Eastern Europe
    {"name": "Romania Journal", "url": "https://www.romaniajournal.ro/feed/", "verticals": ["Agriculture"]},
    {"name": "Budapest Business Journal", "url": "https://bbj.hu/rss.xml", "verticals": ["Agriculture"]},
    {"name": "Emerging Europe", "url": "https://emerging-europe.com/feed/", "verticals": ["Agriculture"]},

    # Fintech / Mainstream
    {"name": "Finextra", "url": "https://www.finextra.com/rss/headlines.aspx", "verticals": ["Mainstream"]},
    {"name": "Pymnts", "url": "https://www.pymnts.com/feed/", "verticals": ["Mainstream"]},
    {"name": "Finance Magnates", "url": "https://www.financemagnates.com/feed/", "verticals": ["Mainstream"]},
]


def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print(f"=== Добавление {len(MISSING_SOURCES)} недостающих источников ===")
    print(f"Database ID: {db_id}\n")

    try:
        # Используем явные имена полей (как при создании базы в setup_notion_sources.py)
        added = 0
        failed = 0

        for source in MISSING_SOURCES:
            try:
                properties = {
                    "Name": {"title": [{"text": {"content": source["name"]}}]},
                    "RSS URL": {"url": source["url"]},
                    "Verticals": {"multi_select": [{"name": v} for v in source["verticals"]]},
                    "Active": {"checkbox": True},
                }

                notion.pages.create(
                    parent={"database_id": db_id},
                    properties=properties
                )
                print(f"  + {source['name']} ({', '.join(source['verticals'])})")
                added += 1
            except Exception as e:
                print(f"  x {source['name']}: {e}")
                failed += 1

        print(f"\nРезультат: добавлено {added}, ошибок {failed}")

    except Exception as e:
        import traceback
        print(f"Ошибка: {e}")
        traceback.print_exc()
    finally:
        http_client.close()


if __name__ == "__main__":
    main()
