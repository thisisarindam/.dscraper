# .dscraper

A lightweight Python scraping project for collecting fashion product data from Rare Rabbit, Bewakoof, and Limeroad.

## Overview
This repository contains experimental scraping scripts that extract product details and images from retail pages and save the results to CSV. The codebase currently includes:
- Selenium-based scraping for Bewakoof and Rare Rabbit
- A Playwright-based Limeroad scraper stub
- Prototype scripts for different extraction approaches and iterative improvements

## Project Status
- `scrape_rare_rabit_dom_process.py` — current Bewakoof scraper variant designed to navigate the men’s clothing page, apply filters, scroll the grid, and save 20 product records.
- `codespace_scraper_bewakoof.py` — another Bewakoof Selenium scraper that captures top 20 items and saves them to CSV.
- `scrape_rare_rabit.py` — Rare Rabbit focused scraper that navigates new arrivals and collects product image URLs.
- `scraper_limeroad.py` — Playwright-based Limeroad scraper stub; requires the API endpoint keyword to capture JSON responses.
- `codespace_scraper.py` / `codespace_scraper_v2.py` — earlier Bewakoof scraping prototypes.

## Current workflow
1. Launch a headless browser session using Selenium or Playwright.
2. Navigate to the target product page.
3. Close popups and optionally apply filters/sorting.
4. Scroll through the page to force lazy-loaded images and product cards to render.
5. Extract product titles, prices, and image URLs.
6. Save the result to a CSV file.

## Recommended scripts
From the project root, use one of the following:

```bash
python scrape_rare_rabit_dom_process.py
```

```bash
python codespace_scraper_bewakoof.py
```

```bash
python scrape_rare_rabit.py
```

```bash
python scraper_limeroad.py
```

## Dependencies
The Selenium-based scripts require:
- selenium
- webdriver-manager

The Limeroad stub requires:
- playwright

Install dependencies with pip:

```bash
pip install selenium webdriver-manager playwright
```

If you use Playwright, remember to install browsers:

```bash
playwright install chromium
```

## Output files
Current outputs produced by the repository include:
- `final_bewakoof_20_tshirts.csv`
- `bewakoof_top_20_new.csv`
- `rare_rabbit_30_tshirts.csv`
- `rare_rabit_scraper_data.csv`
- `bewakoof_top_20_11-06-2026.csv`
- `final_bewakoof_20_tshirts_12-06-2026.csv`

## Notes and progress
- The project has moved from prototype scripts to more robust flow control for Bewakoof, including popup handling, sorting, filter selection, and extra scrolls to load lazy content.
- The Rare Rabbit scraper is currently implemented as a Selenium workflow that gathers up to 30 product image URLs.
- The Limeroad scraper is a network-interception prototype and still requires the correct API endpoint keyword to become fully operational.

## Purpose
This repository is intended for scraping experiments, product catalog data collection, and CSV export for fashion merchandise analysis.
