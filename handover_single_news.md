# Handover Document: Single News Project

**Handover Date:** February 3, 2026
**Project:** News collection automation for client relationship management
**Status:** Working Prototype

---

## 1. Project Goal

Build an automated system that collects news from RSS sources weekly, filters them by relevance for each client, and generates Markdown digests.

---

## 2. Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          NOTION                                 │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │  Clients Profile    │      │   Sources (RSS)     │          │
│  │  for AI (created)   │      │   32 sources across │          │
│  │                     │      │   4 verticals       │          │
│  │                     │      │                     │          │
│  └──────────┬──────────┘      └──────────┬──────────┘          │
└─────────────┼────────────────────────────┼──────────────────────┘
              │         Notion API         │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │       PYTHON SCRIPT          │
              │  1. Load clients             │
              │  2. Load RSS sources         │
              │  3. Match by verticals       │
              │  4. Collect news from RSS    │
              │  5. Score by keywords        │
              │  6. Generate MD digest       │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │     CLAUDE (NOT YET DONE)    │
              │  1. Relevance analysis       │
              │  2. Mark High/Med/Low        │
              │  3. Final digest             │
              │  4. Select top-3 news        │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  GITHUB ACTIONS (NOT YET)    │
              │   Weekly automated run       │
              └──────────────────────────────┘
```

---

## 3. What Has Been Done

### 3.1. Notion

**Integration configured:**
- Name: "Single News for Clients"
- Workspace: Drewsank's Space
- Type: Internal
- Status: Working

**Database "Clients Profile for AI" created** with fields:
| Field | Type |
|-------|------|
| Client Name | Title |
| Verticals | Multi-select (RWA, Agricultural) |
| Jurisdiction | Multi-select |
| Markets | Multi-select |
| Current Issue/Challenge | Rich text |
| Client Interests | Rich text |
| Keywords | Rich text |

**Database "RSS Sources" created** (via Data Source API) with fields:
| Field | Type |
|-------|------|
| Name | Title |
| RSS URL | URL |
| Verticals | Multi-select (RWA, Agriculture, DeFi, Mainstream) |
| Active | Checkbox |

### 3.2. Test Client GT

- **Verticals:** RWA, Agricultural
- **Product:** Platform connecting grain deal participants (banks, elevators, traders). Issues tokenized grain-backed assets and e-WHR for farmer loans.
- **Jurisdiction:** Switzerland (registration), CIS market (focus: Kazakhstan, Romania)
- **Current Challenge:** Finding pilot partner (elevator or financial institution)
- **Keywords:** tokenization, RWA, e-WHR, digital warehouse receipt, commodity-backed token, grain tokenization, agricultural commodities, commodity financing, inventory monitoring, collateral management, agriculture, grain trading, elevator, silo, agritech, agri-finance, trade finance, commodity lending, warehouse financing, collateral verification, Kazakhstan, Romania, CIS, Central Asia, Eastern Europe, Switzerland, grain elevator, commodity trader, agricultural lender, pilot program

### 3.3. RSS Sources (32 total, all in Notion + JSON fallback)

**RWA / Tokenization (10):**
- CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
- The Block: https://www.theblock.co/rss.xml
- The Defiant: https://thedefiant.io/feed
- CryptoSlate: https://cryptoslate.com/feed/
- Cointelegraph: https://cointelegraph.com/rss
- Blockworks: https://blockworks.co/feed/
- Decrypt: https://decrypt.co/feed
- Unchained: https://unchainedcrypto.com/feed/
- DL News: https://www.dlnews.com/arc/outboundfeeds/rss/
- BeInCrypto: https://beincrypto.com/feed/

**RWA Specialized (2):**
- CryptoSlate RWA: https://cryptoslate.com/feed/?post_type=rwa
- CoinDesk RWA: https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tags=real-world-assets

**Agriculture / CIS (8):**
- The Astana Times: https://astanatimes.com/feed/
- World Grain: https://www.world-grain.com/rss
- Grain Central: https://www.graincentral.com/feed/
- AgriCensus: https://www.agricensus.com/feed/
- Agriculture.com: https://www.agriculture.com/feed/
- Ag Funder News: https://agfundernews.com/feed
- Farm Progress: https://www.farmprogress.com/rss.xml
- Time.kz: https://time.kz/rss

**Agriculture / Eastern Europe (4):**
- Romania Insider: https://www.romania-insider.com/feed
- Romania Journal: https://www.romaniajournal.ro/feed/
- Budapest Business Journal: https://bbj.hu/rss.xml
- Emerging Europe: https://emerging-europe.com/feed/

**Commodities (2):**
- Investing.com Commodities: https://www.investing.com/rss/news_14.rss
- Oilprice: https://oilprice.com/rss/main

**Fintech / Mainstream (6):**
- TechCrunch Fintech: https://techcrunch.com/category/fintech/feed/
- TechCrunch Crypto: https://techcrunch.com/category/cryptocurrency/feed/
- Financial Times: https://www.ft.com/rss/home
- Finextra: https://www.finextra.com/rss/headlines.aspx
- Pymnts: https://www.pymnts.com/feed/
- Finance Magnates: https://www.financemagnates.com/feed/

### 3.4. Python Script (`news_collector.py`) — Working

The core script is fully functional and performs:
1. Loads RSS sources from Notion (with JSON fallback if Notion fails)
2. Loads client profiles from Notion
3. Fetches RSS news for the last 7 days (max 20 per source)
4. Filters news by matching verticals between source and client
5. Scores relevance using keyword matching, issue matching, and interest matching
6. Generates Markdown digest with Top-3, High/Medium/Low sections, and statistics
7. Saves digest to `digests/` folder

**Test run result (Jan 29, 2026):** Generated `GT_20260129.md` — 179 articles collected, 7 high / 30 medium / 142 low relevance.

### 3.5. Decisions Made

| Decision | Choice | Reason |
|----------|--------|--------|
| MCP vs API | API (Python script) | MCP requires manual launch, goal is full automation |
| Sources storage | In Notion + JSON fallback | Easy to edit without code access; JSON as safety net |
| Claude integration | Claude API (anthropic SDK) | SDK added to requirements, planned for stage 2 |
| Filtering | Two-stage (planned) | Stage 1: Python keyword scoring (done). Stage 2: Claude AI analysis (not done) |
| HTTP client | httpx | Custom timeouts needed for Notion API calls |

---

## 4. What Is NOT Done

### 4.1. Code
- [ ] Claude API integration for AI-based relevance analysis (anthropic SDK is in requirements.txt but not used in code)
- [ ] GitHub Actions for weekly automation
- [ ] GitHub repository not yet created

### 4.2. Calibration
- [ ] Testing filtering quality — current keyword scoring produces false positives (e.g., oil/gas news scored as High for agri/RWA client)
- [ ] Tuning Keywords for maximum capture of relevant news
- [ ] Verifying all 32 RSS sources are functional and returning data
- [ ] Output digest format needs "Why relevant" field for top-3 news (currently missing)

---

## 5. Roadmap

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | RSS Sources database in Notion: verified sources relevant to test client GT | Done (32 sources loaded) |
| 2 | Python script: RSS news collection, filtering by client Keywords, preliminary Markdown file generation | Done (news_collector.py working) |
| 3 | Final Markdown digest: Claude marks relevance and generates structured report with top-3 news | Not started |
| 4 | Calibrated prompt and Keywords list: news marked as High matches client's actual interests and challenges | Not started |
| 5 | Automated weekly run via GitHub Actions | Not started |

---

## 6. Technical Details

### Project Structure
```
Meszen Single News/
├── .env                        # API keys and DB IDs
├── requirements.txt            # Python dependencies
├── news_collector.py           # Main application
├── sources.json                # JSON fallback (32 sources)
├── new_sources.json            # Additional tested sources
├── add_missing_sources.py      # Script to add sources to Notion
├── setup_notion_sources.py     # DB creation script
├── add_sources.py              # Generic source adder
├── fill_sources_direct.py      # Direct fill with field testing
├── add_via_datasource.py       # Data Source API approach
├── test_notion.py              # Notion connection test
├── test_clients_db.py          # Clients DB test
├── test_new_sources.py         # RSS feed validation
├── check_agro_sources.py       # Agro RSS tests
├── check_sources_db.py         # DB structure check
├── debug_notion.py             # Full DB response dump
└── digests/
    └── GT_20260129.md          # Generated digest for client GT
```

### Required Python Libraries
```
feedparser>=6.0.0     # RSS parsing
notion-client>=2.0.0  # Notion API
python-dotenv>=1.0.0  # Environment variables
anthropic>=0.25.0     # Claude API (not yet used)
httpx                 # HTTP client with custom timeouts
```

### Environment Variables
```
NOTION_API_KEY=secret_...
NOTION_CLIENTS_DB_ID=...
NOTION_SOURCES_DB_ID=...
ANTHROPIC_API_KEY=    # Empty, needs to be filled for Claude integration
```

### Output Digest Format (Current Implementation)
```markdown
# Weekly News Digest: [Client Name]

**Period:** [start date] - [end date]
**Verticals:** [list]
**Markets:** [list]

---

## Top 3 News

### 1. [Title]
**Source:** [source] | **Date:** [date]
[Summary]...
[Read more](url)

---

## High Relevance ([n] articles)
- [Title](url) - *Source*

## Medium Relevance ([n] articles)
- [Title](url) - *Source*

## Low Relevance ([n] articles)
- [Title](url) - *Source*

---

## Statistics
- Total articles collected: [n]
- High relevance: [n]
- Medium relevance: [n]
- Low relevance: [n]
- Sources used: [n]
```

### Relevance Scoring (Current — Python keyword-based)
- **Score >= 6 → High:** Multiple keyword matches + issue/interest matches
- **Score >= 3 → Medium:** Some keyword or interest matches
- **Score < 3 → Low:** Matched only by vertical

### Relevance Scoring (Planned — Claude AI)
- **High:** Related to client's current challenge + matches keywords
- **Medium:** Matches client interests + matches keywords
- **Low:** Only matches vertical

---

## 7. Known Issues

1. **False positives in scoring:** Oilprice/commodities news gets scored as High for GT client because generic words like "capital", "trading" match keywords. Needs Claude AI analysis or more precise keyword tuning.
2. **Notion Data Source API:** The Sources database uses Notion's Data Source API (not standard properties), which makes programmatic access non-trivial. Field name is "Verticals" (not "Vertical").
3. **Some RSS feeds may be broken:** Not all 32 sources have been verified to return data. Need systematic testing.
4. **No deduplication:** Same article from CryptoSlate and CryptoSlate RWA may appear twice in digest.

---

## 8. Access

### Notion
- **Workspace:** Drewsank's Space (personal, test environment)
- **Integration:** "Single News for Clients"
- **Databases:** "Clients Profile for AI", "RSS Sources"

### How to Get Keys
1. **Notion API Key:** https://www.notion.so/my-integrations → Single News for Clients → Show Internal Integration Secret
2. **Database ID:** Database URL, part between last `/` and `?`

### GitHub Repository
Not created yet
