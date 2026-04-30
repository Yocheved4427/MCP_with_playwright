# 🌤️ MCP Weather Forecast — Israel & USA

An AI-powered weather assistant built with the **Model Context Protocol (MCP)**, **OpenAI GPT-4o-mini**, and **Playwright** browser automation.

The project connects an LLM to live weather data through MCP tool servers — one for Israel (Playwright-based web scraping) and one for the USA (NWS REST API).

---

## 🏗️ Architecture

```
User chat
    │
    ▼
host.py  (ChatHost + OpenAI GPT-4o-mini)
    │
    ├── MCP Client ──► weather_Israel.py  (Playwright browser automation)
    │
    └── MCP Client ──► weather_USA.py     (NWS REST API via httpx)
```

---

## 📁 Project Structure

| File | Description |
|---|---|
| `host.py` | Main chat loop — connects MCP clients and calls OpenAI |
| `client.py` | Generic MCP client that manages a stdio server session |
| `weather_Israel.py` | MCP server with 4 Playwright tools for Israeli weather |
| `weather_USA.py` | MCP server with 2 tools for US weather alerts & forecasts |
| `.env.example` | Template for required environment variables |
| `pyproject.toml` | Project dependencies (uv) |

---

## 🛠️ MCP Tools

### 🇮🇱 Israel — `weather_Israel.py`

Uses **Playwright** to automate a real browser session on [weather2day.co.il](https://www.weather2day.co.il).

| Tool | Description |
|---|---|
| `open_Israel_forecast` | Opens Chromium and navigates to the weather site |
| `enter_Israel_city_forecast(city)` | Clicks the search bar and types the city name |
| `select_weather_forecast_city_israel` | Clicks the first autocomplete suggestion |
| `extract_weather_data_israel` | Scrapes and cleans the forecast text from the page |

**Flow:**
```
open_Israel_forecast
    → enter_Israel_city_forecast("תל אביב")
        → select_weather_forecast_city_israel
            → extract_weather_data_israel
```

### 🇺🇸 USA — `weather_USA.py`

Uses the **National Weather Service (NWS) REST API** — no browser needed.

| Tool | Description |
|---|---|
| `get_alerts_in_USA(state)` | Gets active weather alerts for a US state (e.g. `CA`, `NY`) |
| `get_forecast_in_USA(lat, lon)` | Gets a 5-period forecast for a GPS coordinate |

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/Yocheved4427/MCP_with_playwright.git
cd MCP_with_playwright
```

### 2. Install dependencies
Requires [uv](https://docs.astral.sh/uv/).
```bash
uv sync
```

### 3. Install Playwright browsers
```bash
uv run playwright install chromium
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your key:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 5. Run
```bash
uv run host.py
```

---

## 💬 Example Queries

```
Query: What is the weather in Jerusalem today?
Query: Are there any weather alerts in California?
Query: What's the forecast for New York? (lat 40.71, lon -74.00)
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `openai` | GPT-4o-mini LLM |
| `mcp` | Model Context Protocol server/client |
| `playwright` | Browser automation for Israeli weather site |
| `python-dotenv` | Load `.env` file |

---

## 🐍 Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) package manager

