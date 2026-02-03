"""Тест доступа к базе клиентов"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CLIENTS_DB_ID")

    print(f"=== Проверка базы клиентов ===")
    print(f"Database ID: {db_id}\n")

    # Создаем клиент с увеличенным таймаутом
    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    try:
        # Получаем структуру базы
        print("Получаем информацию о базе...")
        db = notion.databases.retrieve(db_id)
        title = db["title"][0]["plain_text"] if db.get("title") else "Без названия"
        print(f"База: {title}")

        # Выводим все поля
        if "properties" in db:
            print(f"\nПоля базы:")
            for name, prop in db["properties"].items():
                print(f"  - {name} ({prop['type']})")
        else:
            print("\nЭто Data Source база. Проверяем data_sources...")
            if "data_sources" in db:
                for ds in db["data_sources"]:
                    print(f"  Data Source ID: {ds['id']}")
                    print(f"  Data Source Name: {ds['name']}")

        # Пробуем запросить данные через data source
        print(f"\n=== Запрос клиентов ===")

        # Для Data Source используем другой endpoint
        data_source_id = db.get("data_sources", [{}])[0].get("id") if db.get("data_sources") else None

        if data_source_id:
            print(f"Используем Data Source: {data_source_id}")
            # Используем data sources query
            results = notion.request(
                path=f"data_sources/{data_source_id}/query",
                method="POST",
                body={}
            )
            print(f"Результат: {results}")
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
