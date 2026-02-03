# Проект: Автоматизация сбора новостей для Investor Relations

## Цель
Автоматически собирать новости из RSS-лент, фильтровать по релевантности для каждого клиента и создавать еженедельные Markdown-дайджесты.

## Архитектура

### Хранение данных (Notion)
1. База "Клиенты" (Clients Profile for AI) — уже существует
   - Client Name (Title)
   - Verticals (Multi-select): RWA, Agricultural
   - Jurisdiction (Text)
   - Markets (Multi-select)
   - Current Issue/Challenge (Text)
   - Client Interests (Text)
   - Keywords (Text)

2. База "Источники" — нужно создать
   - Название (Title)
   - RSS URL (URL)
   - Вертикаль (Multi-select): RWA, Agriculture, DeFi, Mainstream

### Источники новостей (15 штук)

RWA / Токенизация:
- CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
- The Block: https://www.theblock.co/rss.xml
- The Defiant: https://thedefiant.io/feed
- CryptoSlate: https://cryptoslate.com/feed/
- Cointelegraph: https://cointelegraph.com/rss
- Blockworks: https://blockworks.co/feed/

Agriculture:
- The Astana Times: https://astanatimes.com/feed/
- World Grain: https://www.world-grain.com/rss
- Romania Insider: https://www.romania-insider.com/feed
- Grain Central: https://www.graincentral.com/feed/

Mainstream:
- TechCrunch Fintech: https://techcrunch.com/category/fintech/feed/
- TechCrunch Crypto: https://techcrunch.com/category/cryptocurrency/feed/
- Decrypt: https://decrypt.co/feed

### Логика работы скрипта
1. Загрузить всех клиентов из Notion
2. Загрузить все источники из Notion
3. Для каждого клиента:
   - Найти источники по его вертикалям
   - Собрать новости из RSS за последние 7 дней
   - Отправить в Claude API для разметки релевантности
   - Сформировать Markdown-дайджест

### Критерии релевантности
- Высокая: связано с текущей проблемой + совпадает с ключевыми словами
- Средняя: попадает в интересы + совпадает с ключевыми словами
- Низкая: только совпадение по вертикали

### Формат дайджеста
Markdown-файл с секциями:
- Топ-3 новости
- Высокая релевантность
- Средняя релевантность
- Низкая релевантность
- Техническая статистика

## Переменные окружения
- NOTION_API_KEY — ключ интеграции Notion
- ANTHROPIC_API_KEY — ключ Claude API
- NOTION_CLIENTS_DB_ID — ID базы клиентов
- NOTION_SOURCES_DB_ID — ID базы источников (после создания)

## Текущая задача
1. Подключиться к Notion API
2. Проверить доступ к базе клиентов
3. Создать базу "Источники" с нужными полями
4. Заполнить её 15 источниками
5. Написать Python-скрипт для сбора и фильтрации новостей