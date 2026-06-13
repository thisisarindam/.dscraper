from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re

def scrape_rare_custom_workflow():
    print("🚀 Booting up Headless Chrome for the Custom Workflow...")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-IN")
    options.add_argument("--tz=Asia/Kolkata")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    scraped_garments = []
    
    try:
        # Step 1 & 2: Go to site and wait 10 seconds
        target_url = "https://thehouseofrare.com/collections/rr-new-arrivals-for-men"
        print(f"Step 1: Navigating to {target_url}")
        driver.get(target_url)
        
        print("Step 2: Waiting 10 seconds for initial page load...")
        time.sleep(10)
        
        # Kill any pop-ups that triggered during the 10-second wait
        print("Assassinating any newsletter popups...")
        driver.execute_script("""
            document.querySelectorAll('[id*="Klaviyo"], iframe, .newsletter, [class*="popup"], [class*="overlay"]').forEach(e => e.remove());
            document.body.style.overflow = 'auto'; 
        """)
        time.sleep(1)

        # Step 3: Click FILTER (If it exists as a button/drawer toggle)
        print("Step 3: Looking for 'FILTER' button...")
        try:
            filter_btn = driver.find_element(By.XPATH, "//*[self::button or self::span][contains(translate(text(), 'FILTER', 'filter'), 'filter')]")
            driver.execute_script("arguments[0].click();", filter_btn)
            time.sleep(1)
        except:
            print("  - Filter button not found or already open.")

        # Step 4: Click T-SHIRT under Category
        print("Step 4: Attempting to select 'T-SHIRT' category...")
        try:
            # Try to open the Category accordion if closed
            try:
                category_header = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'CATEGORY', 'category'), 'category')]")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category_header)
                driver.execute_script("arguments[0].click();", category_header)
                time.sleep(1)
            except:
                pass 
                
            # Click the actual T-Shirt option
            tshirt_filter = driver.find_element(By.XPATH, "//label[contains(translate(., 'T-SHIRT', 't-shirt'), 't-shirt')] | //a[contains(translate(., 'T-SHIRT', 't-shirt'), 't-shirt')] | //span[contains(translate(., 'T-SHIRT', 't-shirt'), 't-shirt')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tshirt_filter)
            driver.execute_script("arguments[0].click();", tshirt_filter)
            print("  - Successfully clicked T-SHIRT filter.")
        except Exception as e:
            print(f"  ⚠️ Could not click T-Shirt filter: {e}")

        # Step 5: Wait 5 seconds
        print("Step 5: Waiting 5 seconds for filter to apply...")
        time.sleep(5)

        # Step 6: Click SORT BY
        print("Step 6: Attempting to click 'SORT BY'...")
        try:
            sort_btn = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'SORT', 'sort'), 'sort')] | //summary[contains(translate(., 'SORT', 'sort'), 'sort')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sort_btn)
            driver.execute_script("arguments[0].click();", sort_btn)
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Could not click Sort By: {e}")

        # Step 7: Click NEW ARRIVALS
        print("Step 7: Selecting 'NEW ARRIVALS'...")
        try:
            # Shopify often labels this "Date, new to old" or "New Arrivals" depending on the theme
            new_arrival_option = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'NEW ARRIVAL', 'new arrival'), 'new arrival')] | //*[contains(text(), 'new to old')] | //option[contains(translate(text(), 'NEW', 'new'), 'new')]")
            driver.execute_script("arguments[0].click();", new_arrival_option)
            print("  - Successfully selected New Arrivals.")
        except Exception as e:
            print(f"  ⚠️ Could not select New Arrivals: {e}")

        # Step 8: Wait 5 seconds
        print("Step 8: Waiting 5 seconds for sort to apply...")
        time.sleep(5)

        # Scroll to force high-res images to lazy-load
        print("Scrolling down to load high-res images...")
        for i in range(6):
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(2)

        # Step 9: Extract 20 images, prices, and names using the unbreakable JS DOM Scanner
        print("Step 9: Extracting 20 product profiles...")
        
        extracted_data = driver.execute_script("""
            let results = [];
            let seenCards = new Set();
            let seenUrls = new Set();
            
            let links = document.querySelectorAll('a[href*="/products/"]');
            
            links.forEach(link => {
                let href = link.href.split('?')[0];
                let parent = link;
                let hasPrice = false;
                
                for(let i=0; i<6; i++) { 
                    if(parent.parentElement) {
                        parent = parent.parentElement;
                        let text = parent.textContent;
                        if(text.includes('₹') || text.includes('Rs')) {
                            hasPrice = true;
                            break;
                        }
                    }
                }
                
                if(hasPrice && !seenCards.has(parent) && !seenUrls.has(href)) {
                    seenCards.add(parent);
                    seenUrls.add(href);
                    
                    let img = parent.querySelector('img');
                    let imgUrl = img ? (img.getAttribute('data-srcset') || img.getAttribute('srcset') || img.getAttribute('data-src') || img.src) : '';
                    let rawText = parent.innerText || parent.textContent;
                    
                    results.push({
                        image: imgUrl,
                        text: rawText
                    });
                }
            });
            return results;
        """)

        extracted_count = 0
        
        for item in extracted_data:
            if extracted_count >= 20: # Stopped exactly at 20 per your plan
                break
                
            try:
                # Format Image (High Res Scrubber)
                image_url = item['image']
                if image_url:
                    image_url = image_url.split(",")[-1].strip().split(" ")[0] 
                    image_url = image_url.split("?")[0]
                    image_url = re.sub(r'_\d+x\d*', '', image_url)
                    image_url = re.sub(r'_crop_[a-z]+', '', image_url)
                    if image_url.startswith("//"): image_url = "https:" + image_url
                else:
                    continue

                # Format Text & Price
                raw_text = item['text']
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                
                title = "Name not found"
                price = "Price not found"
                
                valid_text_lines = []

                for line in lines:
                    if '₹' in line or 'Rs' in line:
                        if price == "Price not found":
                            price = "₹" + "".join(char for char in line if char.isdigit() or char == ',')
                    else:
                        if len(line) > 2 and line.upper() not in ["NEW", "SALE", "SOLD OUT", "ADD TO CART", "QUICK VIEW"]:
                            valid_text_lines.append(line)
                            
                if len(valid_text_lines) >= 1:
                    title = valid_text_lines[0]

                if title == "Name not found" and price == "Price not found":
                    continue

                print(f"Extracted {extracted_count + 1}/20: {title} | {price}")
                
                scraped_garments.append({
                    "Product_Name": title,
                    "Price": price,
                    "Image_URL": image_url
                })
                
                extracted_count += 1
                
            except Exception as e:
                pass 

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        
    # Step 10: Save to CSV
    if scraped_garments:
        output_filename = "rare_rabit_scraper_data.csv"
        print(f"Step 10: 💾 Saving {len(scraped_garments)} garments to {output_filename}...")
        keys = scraped_garments[0].keys()
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(scraped_garments)
        print("✅ Data extraction successfully completed!")

if __name__ == "__main__":
    scrape_rare_custom_workflow()