"""Тест подключения к Notion API и поиск баз данных"""
import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

def main():
    api_key = os.getenv("NOTION_API_KEY")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

    notion = Client(auth=api_key)

    print("\n=== Подключение к Notion ===\n")

    # Проверяем пользователя
    try:
        me = notion.users.me()
        print(f"Интеграция: {me.get('name', 'N/A')}")
        print(f"Тип: {me.get('type', 'N/A')}")
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")

    # Поиск всех объектов
    print("\nПоиск доступных объектов...")
    try:
        results = notion.search()
        print(f"Всего найдено объектов: {len(results['results'])}")

        for item in results["results"]:
            obj_type = item["object"]
            if obj_type == "database":
                title = item["title"][0]["plain_text"] if item.get("title") else "Без названия"
                print(f"\n[DATABASE] {title}")
                print(f"   ID: {item['id']}")
                props = list(item.get("properties", {}).keys())
                print(f"   Поля: {', '.join(props[:5])}{'...' if len(props) > 5 else ''}")
            elif obj_type == "page":
                title_prop = item.get("properties", {}).get("title", {})
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"] if title_prop["title"] else "Без названия"
                else:
                    title = "Страница"
                print(f"\n[PAGE] {title}")
                print(f"   ID: {item['id']}")

    except Exception as e:
        print(f"Ошибка поиска: {e}")

if __name__ == "__main__":
    main()
