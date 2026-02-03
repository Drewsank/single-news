"""Добавление источников через Data Source API"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

# RSS источники
RSS_SOURCES = [
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "verticals": ["RWA", "DeFi"]},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed", "verticals": ["RWA", "DeFi"]},
    {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "verticals": ["RWA", "DeFi"]},
    {"name": "Blockworks", "url": "https://blockworks.co/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Astana Times", "url": "https://astanatimes.com/feed/", "verticals": ["Agriculture"]},
    {"name": "World Grain", "url": "https://www.world-grain.com/rss", "verticals": ["Agriculture"]},
    {"name": "Romania Insider", "url": "https://www.romania-insider.com/feed", "verticals": ["Agriculture"]},
    {"name": "Grain Central", "url": "https://www.graincentral.com/feed/", "verticals": ["Agriculture"]},
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/", "verticals": ["Mainstream"]},
    {"name": "TechCrunch Crypto", "url": "https://techcrunch.com/category/cryptocurrency/feed/", "verticals": ["RWA", "DeFi", "Mainstream"]},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "verticals": ["RWA", "DeFi", "Mainstream"]},
]

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print(f"=== Добавление источников ===")
    print(f"Database ID: {db_id}\n")

    try:
        # Получаем data source ID
        db = notion.databases.retrieve(db_id)
        data_sources = db.get("data_sources", [])

        if data_sources:
            ds_id = data_sources[0]["id"]
            print(f"Data Source ID: {ds_id}\n")

            # Пробуем добавить через data source
            for source in RSS_SOURCES:
                try:
                    result = notion.request(
                        path=f"data_sources/{ds_id}/records",
                        method="POST",
                        body={
                            "Name": source["name"],
                            "RSS URL": source["url"],
                            "Vertical": source["verticals"],
                        }
                    )
                    print(f"  + {source['name']}")
                except Exception as e:
                    print(f"  x {source['name']}: {e}")
                    break
        else:
            print("Data Source не найден")

    except Exception as e:
        import traceback
        print(f"Ошибка: {e}")
        traceback.print_exc()
    finally:
        http_client.close()

if __name__ == "__main__":
    main()
