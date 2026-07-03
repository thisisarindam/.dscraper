# .dscraper

Fashion product web scraper for Bewakoof, Rare Rabbit, and Limeroad.

## Tech Stack
- **Bewakoof & Rare Rabbit**: Selenium + webdriver-manager
- **Limeroad**: Playwright (network interception stub)

## Scripts
| `scrape_rare_rabit_dom_process.py` | Bewakoof men's clothing | CSV (20 items) |
| `codespace_scraper_bewakoof.py` | Bewakoof | CSV (top 20) |
| `scrape_rare_rabit.py` | Rare Rabbit new arrivals | CSV (product URLs) |
| `scraper_limeroad.py` | Limeroad (needs API keyword) | JSON via network interception |

## Quick Start
```bash
pip install selenium webdriver-manager playwright
playwright install chromium

python scrape_rare_rabit_dom_process.py
```

## Features
- Popup handling, filter application, sorting
- Lazy-load scrolling
- CSV export of product titles, prices, images
- Headless browser execution
