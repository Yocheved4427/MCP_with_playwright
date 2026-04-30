from mcp.server.fastmcp import FastMCP
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/jerusalem"

# Global browser state — persists across tool calls within the same process
_playwright = None
_browser = None
_page = None


@mcp.tool()
async def open_Israel_forecast() -> str:
    """Opens the browser and navigates to the Israeli weather forecast website."""
    global _playwright, _browser, _page

    if _browser is not None:
        try:
            await _browser.close()
        except Exception:
            pass

    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch(headless=False)
    _page = await _browser.new_page()
    await _page.goto(FORECAST_URL)
    await _page.wait_for_load_state("domcontentloaded")
    return f"Browser opened and navigated to {FORECAST_URL}"


@mcp.tool()
async def enter_Israel_city_forecast(city: str) -> str:
    """Enters a city name into the search field on the Israeli weather website.

    Args:
        city: The name of the Israeli city to search for (Hebrew or English)
    """
    global _page

    if _page is None:
        return "Error: Browser is not open. Call open_Israel_forecast first."

    # Click the location widget to reveal the search input
    await _page.click("#location-search")
    await _page.wait_for_timeout(400)

    # Clear and type the city name
    await _page.fill("#city_search", "")
    await _page.type("#city_search", city, delay=80)

    # Wait for the autocomplete list to appear
    try:
        await _page.wait_for_selector(
            "#city_searchautocomplete-list div",
            state="visible",
            timeout=5000,
        )
        return f"City '{city}' entered. Autocomplete suggestions are ready."
    except PlaywrightTimeout:
        return f"City '{city}' entered but no autocomplete suggestions appeared."


@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """Selects the first city from the autocomplete suggestion list on the weather website."""
    global _page

    if _page is None:
        return "Error: Browser is not open. Call open_Israel_forecast first."

    try:
        first_item = _page.locator("#city_searchautocomplete-list div").first
        await first_item.wait_for(state="visible", timeout=5000)
        city_text = await first_item.inner_text()
        await first_item.click()
        await _page.wait_for_load_state("domcontentloaded")
        return f"Selected city: '{city_text.strip()}'. Weather page loaded."
    except PlaywrightTimeout:
        return "Error: No autocomplete suggestions found. Enter a city first."


@mcp.tool()
async def extract_weather_data_israel() -> str:
    """Extracts and returns the weather forecast text from the currently open weather page.

    Reads visible text from the main content area of the Israeli weather site,
    cleans it up, and returns a concise string for the LLM to answer the user's question.

    Returns:
        A cleaned string with the weather forecast data from the open page.
    """
    global _page

    if _page is None:
        return "Error: Browser is not open. Call open_Israel_forecast first."

    # Target the main content container; fall back to body if not found
    try:
        raw_text = await _page.inner_text("main")
    except Exception:
        raw_text = await _page.inner_text("body")

    # Remove lines that are pure navigation / boilerplate (short or link-heavy)
    lines = raw_text.splitlines()
    cleaned_lines: list[str] = []
    skip_keywords = (
        "פרטיות", "תנאי שימוש", "צור קשר", "בעלי אתרים", "אודות האתר",
        "פרימיום", "שדרג עכשיו", "עוגיות", "©",
    )
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < 3:
            continue
        if any(kw in stripped for kw in skip_keywords):
            continue
        cleaned_lines.append(stripped)

    # Collapse repeated blank lines that survived
    result = "\n".join(cleaned_lines)

    # Truncate to ~4000 chars to stay within token budget
    if len(result) > 4000:
        result = result[:4000] + "\n...[truncated]"

    return result


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
