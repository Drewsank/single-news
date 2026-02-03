"""
Сбор новостей из RSS и создание дайджестов для клиентов
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from notion_client import Client
import feedparser
import httpx

load_dotenv()


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    published: datetime
    source: str
    verticals: List[str]


@dataclass
class Client_:
    name: str
    verticals: List[str]
    jurisdiction: str
    markets: List[str]
    current_issue: str
    interests: str
    keywords: List[str]


def load_sources() -> List[Dict]:
    """Загрузка источников из Notion"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_SOURCES_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    sources = []

    try:
        # Получаем data source ID
        db = notion.databases.retrieve(db_id)
        data_sources = db.get("data_sources", [])

        if not data_sources:
            print("    Sources Data Source not found, using JSON fallback")
            return load_sources_json()

        ds_id = data_sources[0]["id"]

        # Запрашиваем записи
        results = notion.request(
            path=f"data_sources/{ds_id}/query",
            method="POST",
            body={}
        )

        for page in results.get("results", []):
            props = page.get("properties", {})

            name = ""
            url = ""
            verticals = []
            active = True

            for prop_name, prop in props.items():
                if prop["type"] == "title" and prop.get("title"):
                    name = prop["title"][0]["plain_text"] if prop["title"] else ""
                elif prop_name == "RSS URL" and prop.get("url"):
                    url = prop["url"]
                elif prop_name == "Verticals" and prop.get("multi_select"):
                    verticals = [v["name"] for v in prop["multi_select"]]
                elif prop_name == "Active" and prop["type"] == "checkbox":
                    active = prop.get("checkbox", True)

            if name and url and active:
                sources.append({
                    "name": name,
                    "url": url,
                    "verticals": verticals
                })

    except Exception as e:
        print(f"    Error loading sources from Notion: {e}")
        return load_sources_json()
    finally:
        http_client.close()

    return sources


def load_sources_json() -> List[Dict]:
    """Fallback: загрузка источников из JSON"""
    path = os.path.join(os.path.dirname(__file__), "sources.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data["sources"] if s.get("active", True)]


def load_clients() -> List[Client_]:
    """Загрузка клиентов из Notion"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CLIENTS_DB_ID")

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    clients = []

    try:
        # Получаем data source ID
        db = notion.databases.retrieve(db_id)
        data_sources = db.get("data_sources", [])

        if not data_sources:
            print("Data Source не найден")
            return clients

        ds_id = data_sources[0]["id"]

        # Запрашиваем записи
        results = notion.request(
            path=f"data_sources/{ds_id}/query",
            method="POST",
            body={}
        )

        for page in results.get("results", []):
            props = page.get("properties", {})

            # Извлекаем данные
            name = ""
            verticals = []
            jurisdiction = ""
            markets = []
            current_issue = ""
            interests = ""
            keywords = []

            for prop_name, prop in props.items():
                if prop["type"] == "title" and prop.get("title"):
                    name = prop["title"][0]["plain_text"] if prop["title"] else ""
                elif prop_name == "Verticals" and prop.get("multi_select"):
                    verticals = [v["name"] for v in prop["multi_select"]]
                elif prop_name == "Jurisdiction" and prop.get("multi_select"):
                    jurisdiction = ", ".join(v["name"] for v in prop["multi_select"])
                elif prop_name == "Markets" and prop.get("multi_select"):
                    markets = [v["name"] for v in prop["multi_select"]]
                elif prop_name == "Current Issue/Challenge" and prop.get("rich_text"):
                    current_issue = prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
                elif prop_name == "Client Interests" and prop.get("rich_text"):
                    interests = prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
                elif prop_name == "Keywords" and prop.get("rich_text"):
                    kw_text = prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
                    keywords = [k.strip().lower() for k in kw_text.split(",") if k.strip()]

            if name:
                clients.append(Client_(
                    name=name,
                    verticals=verticals,
                    jurisdiction=jurisdiction,
                    markets=markets,
                    current_issue=current_issue,
                    interests=interests,
                    keywords=keywords
                ))

    except Exception as e:
        print(f"Ошибка загрузки клиентов: {e}")
    finally:
        http_client.close()

    return clients


def fetch_rss_news(sources: List[Dict], days: int = 7) -> List[NewsItem]:
    """Сбор новостей из RSS за последние N дней"""
    news = []
    cutoff = datetime.now() - timedelta(days=days)

    for source in sources:
        print(f"  Загрузка: {source['name']}...")
        try:
            feed = feedparser.parse(source["url"])

            for entry in feed.entries[:20]:  # Максимум 20 записей с источника
                # Парсим дату
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    published = datetime.now()

                if published < cutoff:
                    continue

                # Получаем summary
                summary = ""
                if hasattr(entry, "summary"):
                    # Убираем HTML теги
                    summary = re.sub(r"<[^>]+>", "", entry.summary)[:500]

                news.append(NewsItem(
                    title=entry.title,
                    link=entry.link,
                    summary=summary,
                    published=published,
                    source=source["name"],
                    verticals=source["verticals"]
                ))

        except Exception as e:
            print(f"    Ошибка: {e}")

    return news


def filter_news_for_client(news: List[NewsItem], client: Client_) -> List[NewsItem]:
    """Фильтрация новостей по вертикалям клиента"""
    # Находим пересечение вертикалей
    client_verticals_lower = [v.lower() for v in client.verticals]

    filtered = []
    for item in news:
        item_verticals_lower = [v.lower() for v in item.verticals]
        if any(v in client_verticals_lower for v in item_verticals_lower):
            filtered.append(item)
        elif "mainstream" in item_verticals_lower:
            # Mainstream новости показываем всем
            filtered.append(item)

    return filtered


def score_relevance(news_item: NewsItem, client: Client_) -> tuple:
    """
    Оценка релевантности новости для клиента
    Возвращает (score, level) где level: high, medium, low
    """
    text = (news_item.title + " " + news_item.summary).lower()

    score = 0
    reasons = []

    # Проверяем ключевые слова
    keyword_matches = sum(1 for kw in client.keywords if kw in text)
    if keyword_matches > 0:
        score += keyword_matches * 2
        reasons.append(f"{keyword_matches} keywords")

    # Проверяем текущую проблему клиента
    if client.current_issue:
        issue_words = [w.lower() for w in client.current_issue.split() if len(w) > 4]
        issue_matches = sum(1 for w in issue_words if w in text)
        if issue_matches > 0:
            score += issue_matches * 3
            reasons.append("matches issue")

    # Проверяем интересы
    if client.interests:
        interest_words = [w.lower() for w in client.interests.split() if len(w) > 4]
        interest_matches = sum(1 for w in interest_words if w in text)
        if interest_matches > 0:
            score += interest_matches * 2
            reasons.append("matches interests")

    # Определяем уровень
    if score >= 6:
        level = "high"
    elif score >= 3:
        level = "medium"
    else:
        level = "low"

    return score, level


def generate_digest(client: Client_, news: List[NewsItem]) -> str:
    """Генерация Markdown дайджеста для клиента"""
    now = datetime.now()
    week_start = now - timedelta(days=7)

    # Сортируем и классифицируем новости
    scored_news = []
    for item in news:
        score, level = score_relevance(item, client)
        scored_news.append((item, score, level))

    # Сортируем по score
    scored_news.sort(key=lambda x: x[1], reverse=True)

    # Разделяем по уровням
    high = [(n, s) for n, s, l in scored_news if l == "high"]
    medium = [(n, s) for n, s, l in scored_news if l == "medium"]
    low = [(n, s) for n, s, l in scored_news if l == "low"]

    # Генерируем markdown
    md = f"""# Weekly News Digest: {client.name}

**Period:** {week_start.strftime('%Y-%m-%d')} - {now.strftime('%Y-%m-%d')}
**Verticals:** {', '.join(client.verticals)}
**Markets:** {', '.join(client.markets)}

---

## Top 3 News

"""
    # Топ-3
    for i, (item, score, level) in enumerate(scored_news[:3], 1):
        md += f"""### {i}. {item.title}
**Source:** {item.source} | **Date:** {item.published.strftime('%Y-%m-%d')}
{item.summary[:300]}...
[Read more]({item.link})

"""

    # Высокая релевантность
    if high:
        md += f"""---

## High Relevance ({len(high)} articles)

"""
        for item, score in high[:10]:
            md += f"- [{item.title}]({item.link}) - *{item.source}*\n"

    # Средняя релевантность
    if medium:
        md += f"""
## Medium Relevance ({len(medium)} articles)

"""
        for item, score in medium[:15]:
            md += f"- [{item.title}]({item.link}) - *{item.source}*\n"

    # Низкая релевантность
    if low:
        md += f"""
## Low Relevance ({len(low)} articles)

"""
        for item, score in low[:10]:
            md += f"- [{item.title}]({item.link}) - *{item.source}*\n"

    # Статистика
    md += f"""
---

## Statistics

- Total articles collected: {len(news)}
- High relevance: {len(high)}
- Medium relevance: {len(medium)}
- Low relevance: {len(low)}
- Sources used: {len(set(n.source for n in news))}

*Generated: {now.strftime('%Y-%m-%d %H:%M')}*
"""

    return md


def main():
    print("=" * 50)
    print("NEWS COLLECTOR FOR INVESTOR RELATIONS")
    print("=" * 50)

    # Загружаем источники
    print("\n[1] Loading RSS sources...")
    sources = load_sources()
    print(f"    Loaded {len(sources)} sources")

    # Загружаем клиентов
    print("\n[2] Loading clients from Notion...")
    clients = load_clients()
    print(f"    Loaded {len(clients)} clients")

    if not clients:
        print("\nNo clients found. Exiting.")
        return

    # Собираем новости
    print("\n[3] Fetching RSS news (last 7 days)...")
    all_news = fetch_rss_news(sources, days=7)
    print(f"    Collected {len(all_news)} articles")

    # Создаем папку для дайджестов
    output_dir = os.path.join(os.path.dirname(__file__), "digests")
    os.makedirs(output_dir, exist_ok=True)

    # Генерируем дайджесты
    print("\n[4] Generating digests...")
    for client in clients:
        print(f"    Processing: {client.name}")

        # Фильтруем новости по вертикалям
        client_news = filter_news_for_client(all_news, client)
        print(f"      Filtered: {len(client_news)} articles")

        # Генерируем дайджест
        digest = generate_digest(client, client_news)

        # Сохраняем
        filename = f"{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(digest)
        print(f"      Saved: {filename}")

    print("\n" + "=" * 50)
    print("DONE! Check the 'digests' folder.")
    print("=" * 50)


if __name__ == "__main__":
    main()
