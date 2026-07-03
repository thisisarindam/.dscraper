import json
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_snitch_interceptor():
    print("🚀 Booting up Playwright (The Snitch Wiretap)...")
    scraped_data = []
    seen_names = set()

    # ==========================================
    # THE RECURSIVE DATA HUNTER 
    # (Tuned specifically for Shopify/Headless JSON structures)
    # ==========================================
    def extract_data(obj):
        if isinstance(obj, dict):
            # Hunt for titles and prices
            title = obj.get("title") or obj.get("name")
            price = obj.get("price")
            
            # Shopify often hides prices inside a "variants" list
            if not price and "variants" in obj and isinstance(obj["variants"], list) and len(obj["variants"]) > 0:
                if isinstance(obj["variants"][0], dict):
                    price = obj["variants"][0].get("price")

            # Hunt for images
            image = obj.get("featured_image") or obj.get("image") or obj.get("src")
            if not image and "images" in obj and isinstance(obj["images"], list) and len(obj["images"]) > 0:
                image = obj["images"][0] 
                if isinstance(image, dict):
                    image = image.get("src") or image.get("url")

            # If we found all three, package it up!
            if title and price and image and isinstance(image, str) and isinstance(title, str):
                # Clean up Shopify image formatting
                if "http" not in image and "//" in image:
                    image = "https:" + image
                    
                if title not in seen_names and ("jpg" in image.lower() or "webp" in image.lower() or "png" in image.lower()):
                    clean_price = f"₹{price}" if not str(price).startswith("₹") else str(price)
                    scraped_data.append({
                        "Thumbnail_Image_URL": image.split('?')[0],
                        "Product_Name": title.strip(),
                        "Price": clean_price,
                        "Extraction_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    seen_names.add(title)
                    print(f"  📡 [INTERCEPTED] {len(scraped_data)}: {title[:30]}... | {clean_price}")
            
            # Keep digging deeper into the JSON
            for v in obj.values():
                extract_data(v)
                
        elif isinstance(obj, list):
            for item in obj:
                extract_data(item)

    # ==========================================
    # THE NETWORK WIRETAP
    # ==========================================
    def handle_response(response):
        if "json" in response.headers.get("content-type", "") and response.status == 200:
            try:
                data = response.json()
                extract_data(data)
            except:
                pass

    # ==========================================
    # MAIN EXECUTION
    # ==========================================
    with sync_playwright() as p:
        # Headless is FALSE. A browser will open so you can watch.
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Attach the wiretap
        page.on("response", handle_response)

        # Bypass the click completely by targeting the likely Shopify collection URL
        target_url = "https://www.snitch.co.in/collections/printed-t-shirts"
        print(f"Step 1: Navigating directly to {target_url}")
        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)

        print("Step 2: Waiting 5 seconds for initial APIs to fire...")
        page.wait_for_timeout(5000)

        # ==========================================
        # THE SOURCE CODE RIPPER (Fallback)
        # ==========================================
        print("Step 3: Scanning hidden source code for baked-in JSON databases...")
        try:
            # Rips open Next.js or Shopify inline script tags
            hidden_data = page.evaluate("""
                () => {
                    let data = [];
                    document.querySelectorAll('[type="application/json"], #__NEXT_DATA__').forEach(script => {
                        if(script.innerText.includes('price') && script.innerText.includes('title')) {
                            try { data.push(JSON.parse(script.innerText)); } catch(e) {}
                        }
                    });
                    return data;
                }
            """)
            if hidden_data:
                print("  - 🧬 Detected hidden database in HTML! Extracting...")
                extract_data(hidden_data)
        except:
            pass

        print("Step 4: Scrolling to force background API network traffic...")
        # Since headless=False, if the page loaded the wrong category, 
        # YOU CAN MANUALLY CLICK THE BUTTON in the browser right now, and the script will catch it!
        for i in range(8): 
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(3500)

        browser.close()

    if scraped_data:
        filename = "snitch_graphic_tees_api.csv"
        print(f"\nStep 5: 💾 Packaging data. Saving {len(scraped_data)} garments to {filename}...")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=scraped_data[0].keys())
            writer.writeheader()
            writer.writerows(scraped_data)
        print("✅ Data extraction successfully completed!")
    else:
        print("⚠️ Still 0 products. We need to do manual Network Reconnaissance.")

if __name__ == "__main__":
    scrape_snitch_interceptor()