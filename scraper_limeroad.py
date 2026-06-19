from playwright.sync_api import sync_playwright
import csv
import json

# The keyword you found in Step 1 that identifies the product API request
API_ENDPOINT_KEYWORD = "insert_api_keyword_here" 
TARGET_URL = "https://www.limeroad.com/mens-clothing/t-shirts/oversized-t-shirts"

def run():
    with sync_playwright() as p:
        # Launch headless Chromium. 
        browser = p.chromium.launch(headless=True)
        
        # Setting a realistic user agent helps bypass basic headless detection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        collected_products = []

        # ---------------------------------------------------------
        # Network Interception Handler
        # ---------------------------------------------------------
        def handle_response(response):
            # Listen specifically for successful XHR/Fetch requests to the target API
            if API_ENDPOINT_KEYWORD in response.url and response.status == 200:
                try:
                    json_data = response.json()
                    
                    # NOTE: You must adjust the keys below based on the actual JSON 
                    # structure you observed in the Network tab.
                    products = json_data.get('products', []) 
                    
                    for prod in products:
                        # Check for the "New" badge directly in the JSON data
                        badges = prod.get('badges', [])
                        is_new = any(badge.lower() == 'new' for badge in badges)
                        
                        if is_new and len(collected_products) < 30:
                            collected_products.append({
                                'Product Name': prod.get('name', 'N/A'),
                                'Price': prod.get('price', 'N/A'),
                                'Image URL': prod.get('image_url', 'N/A')
                            })
                except json.JSONDecodeError:
                    pass

        # Attach the listener to the page
        page.on("response", handle_response)

        # ---------------------------------------------------------
        # Navigate and Trigger Data Load
        # ---------------------------------------------------------
        print("Navigating to Limeroad...")
        # Note: If sorting by "New" can be done via URL parameters, append it to TARGET_URL
        # Example: TARGET_URL + "?sort=new"
        page.goto(TARGET_URL, wait_until="networkidle")

        # If URL parameters don't sort by new, you can safely interact with the DOM here.
        # Playwright auto-waits for elements to be actionable, but since we rely on the 
        # network, we just need to trigger the click.
        # page.locator("text='Sort by'").click()
        # page.locator("text='New'").click()

        # Scroll to trigger lazy-loading/pagination if 30 "New" items aren't on the first load
        while len(collected_products) < 30:
            print(f"Collected {len(collected_products)}/30 'New' products. Scrolling...")
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000) # Give the API time to respond

        # ---------------------------------------------------------
        # Output to CSV
        # ---------------------------------------------------------
        csv_filename = "limeroad_new_oversized_tees.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['Product Name', 'Price', 'Image URL'])
            writer.writeheader()
            for item in collected_products[:30]:
                writer.writerow(item)
                
        print(f"Successfully saved 30 products to {csv_filename}")
        browser.close()

if __name__ == "__main__":
    run()