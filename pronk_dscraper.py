import requests
from bs4 import BeautifulSoup
import os
import csv
import time

BASE = "https://pronk.in"
COLLECTION = "/collections/men-oversized-t-shirt"
SORT_QUERY = "?sort_by=created-descending"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; pronk-scraper/1.0)"
}


def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def download_image(url, dest_folder, name_hint=None):
    ensure_dir(dest_folder)
    resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
    resp.raise_for_status()
    ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    fname = (name_hint or str(int(time.time()*1000))) + ext
    path = os.path.join(dest_folder, fname)
    with open(path, "wb") as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)
    return path


def parse_collection():
    url = BASE + COLLECTION + SORT_QUERY
    soup = get_soup(url)

    # find product links
    products = []
    # common patterns: product-card, grid-item, product-grid-item
    for a in soup.select("a[href*='/products/']"):
        href = a.get('href')
        if href and '/products/' in href:
            full_url = BASE + href.split('?')[0]
            products.append(full_url)

    # deduplicate while preserving order
    seen = set()
    product_urls = []
    for p in products:
        if p not in seen:
            seen.add(p)
            product_urls.append(p)

    return product_urls


def parse_product(product_url):
    soup = get_soup(product_url)
    # title
    title = None
    title_tag = soup.find('meta', property='og:title') or soup.find('h1')
    if title_tag:
        title = title_tag.get('content') if title_tag.name == 'meta' else title_tag.get_text(strip=True)

    # price: look for meta or price classes
    price = None
    price_meta = soup.find('meta', property='product:price:amount')
    if price_meta:
        price = price_meta.get('content')
    else:
        # find a price-looking element
        p = soup.select_one('.price, .product__price, .product-single__price')
        if p:
            price = p.get_text(strip=True)

    # image: prefer og:image
    image_url = None
    og = soup.find('meta', property='og:image')
    if og and og.get('content'):
        image_url = og.get('content')
    else:
        # fallback to first product img
        img = soup.select_one('img')
        if img:
            image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
    
    # Ensure HTTPS for all image URLs (Shopify serves both HTTP and HTTPS)
    if image_url and image_url.startswith('http://'):
        image_url = image_url.replace('http://', 'https://', 1)

    return {
        'title': title or '',
        'price': price or '',
        'image_url': image_url or '',
        'product_url': product_url,
    }


def main():
    out_csv = 'pronk_products.csv'
    img_dir = 'images'
    print(f"Fetching collection from {BASE + COLLECTION + SORT_QUERY}...")
    product_urls = parse_collection()
    print(f"Found {len(product_urls)} products")
    rows = []

    for idx, pu in enumerate(product_urls, 1):
        try:
            print(f"Processing product {idx}/{len(product_urls)}: {pu}")
            data = parse_product(pu)
            img_url = data['image_url']
            img_path = ''
            if img_url:
                img_path = download_image(img_url, img_dir, name_hint=f"prod_{idx}")
            rows.append({
                'filename': os.path.basename(img_path) if img_path else '',
                'title': data['title'],
                'price': data['price'],
                'image_url': img_url,
                'product_url': pu,
            })
        except Exception:
            continue
        time.sleep(1)

    # write CSV
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'title', 'price', 'image_url', 'product_url'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Saved {len(rows)} products to {out_csv}")


if __name__ == '__main__':
    main()
