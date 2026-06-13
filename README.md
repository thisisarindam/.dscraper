# .dscraper

A lightweight scraping project for collecting product data from fashion websites such as Rare Rabbit and Bewakoof.

## Overview
Lightweight Python scrapers that extract product name, price, and image URL from Rare Rabbit and Bewakoof store feeds and export results to CSV. The primary script targets Rare Rabbit new-arrival men's T-shirts using the store's Shopify JSON feed.

## What is included
- `scrape_rare_rabit_dom_process.py` — current main scraper for Rare Rabbit men’s new-arrival T-shirt data
- `scrape_rare_rabit.py` — older Selenium-based Rare Rabbit scraper attempt
- `codespace_scraper.py` — older Bewakoof scraper prototype
- `codespace_scraper_v2.py` — improved Bewakoof scraper prototype
- Output CSV files such as `rare_rabbit_men_new_arrival_tshirts.csv`

## Current workflow
1. Fetch product data from the site’s live Shopify JSON feed.
2. Filter for men-only T-shirts.
3. Keep only products marked as new arrivals.
4. Save the result as a CSV with:
   - Product_Name
   - Price
   - Image_URL

## How to run
From the project root:

```bash
python scrape_rare_rabit_dom_process.py
```

If you want to use the same interpreter configured in this workspace, run:

```bash
/home/codespace/.python/current/bin/python scrape_rare_rabit_dom_process.py
```

## Dependencies
The current main script uses Python standard libraries plus:
- `requests`

Older Selenium scripts may also require:
- `selenium`
- `webdriver-manager`

Install them with:

```bash
pip install requests selenium webdriver-manager
```

## Output
The scraper writes CSV files into the project root, for example:
- `rare_rabbit_men_new_arrival_tshirts.csv`

## Notes
- The direct Rare Rabbit collection URL may not load reliably in the browser path, so the current implementation uses the store’s JSON feed instead.
- The exact number of items returned may vary depending on what is available in the live feed at the time of execution.

## Purpose
This project is intended for scraping experiments, data collection, and CSV export for product catalog analysis.
