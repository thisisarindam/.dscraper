from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def run_master_scraper(url, output_filename):
    print("🚀 Booting up Headless Chrome for the final run...")
    
    # Cloud-Safe Configurations
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    scraped_garments = []
    
    try:
        print(f"Navigating to base URL: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2) 
        
        # 1. Close Potential Popups
        print("Checking for subscription alert...")
        try:
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[self::button or self::span or self::a][normalize-space()='NO' or normalize-space()='No']"))
            )
            driver.execute_script("arguments[0].click();", no_button)
            print("Closed subscription alert.")
            time.sleep(1)
        except Exception:
            print("No subscription alert detected.")

        # 2. Sort By: New Arrivals
        print("Attempting to sort by 'New Arrivals'...")
        try:
            sort_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'SORT BY', 'sort by'), 'sort by')] | //div[contains(@class, 'sort-')]"))
            )
            driver.execute_script("arguments[0].click();", sort_button)
            time.sleep(1) 
            
            new_arrival_option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'new')]"))
            )
            driver.execute_script("arguments[0].click();", new_arrival_option)
            print("Selected 'New Arrivals'. Waiting for grid to refresh...")
            time.sleep(4) 
        except Exception as e:
            print("⚠️ Could not sort. Continuing with default layout...")

        # 3. Filter By: T-Shirt
        print("Attempting to apply the 'T-Shirt' filter...")
        try:
            try:
                category_header = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[self::span or self::div][translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='category']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category_header)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", category_header)
                print("Expanded 'Category' accordion.")
                time.sleep(1)
            except Exception:
                pass # Already open or missing

            tshirt_option = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 't-shirt')] | //div[contains(@class, 'filter')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 't-shirt')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tshirt_option)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", tshirt_option)
            print("Successfully clicked the T-Shirt category option.")
            time.sleep(4) 
        except Exception as e:
            print("⚠️ Could not apply T-Shirt filter. Taking screenshot...")
            driver.save_screenshot("filter_error.png")

        # 4. Scroll for Lazy-Loaded Images
        print("Scrolling down to force high-res images to load...")
        for i in range(8):
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(2.5) 
            
        # 5. Extract exactly 20 items
        print("Locating garments...")
        products = driver.find_elements(By.CSS_SELECTOR, "section[data-testid^='product-card-'], div.productCardBox, div.plp-product-card")
        
        print(f"Found {len(products)} product cards. Extracting exactly 20...")
        
        for index, product in enumerate(products[:20]):
            try:
                # Extract Image URL
                image_element = product.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("src")
                if not image_url or "placeholder" in image_url.lower() or image_url.startswith("data:image"):
                    image_url = image_element.get_attribute("data-src") or image_url

                # Extract Title
                try:
                    title_element = product.find_element(By.XPATH, ".//h2 | .//h3 | .//*[@data-testid='product-title']")
                    title = title_element.text.strip()
                except:
                    title = "Title not found"

                # Extract Price
                try:
                    price_element = product.find_element(By.XPATH, ".//div[contains(@class, 'discountedPriceText')] | .//span[contains(text(), '₹')]")
                    price = price_element.text.strip()
                except:
                    price = "Price not found"
                
                print(f"Extracted {index + 1}/20: {title} | {price}")
                
                scraped_garments.append({
                    "Title": title,
                    "Price": price,
                    "Image_URL": image_url
                })
                
            except Exception as e:
                print(f"⚠️ Skipped item {index + 1}: Data missing.")

    except Exception as e:
        print(f"❌ Critical Error! {e}")
        
    finally:
        print("Closing browser...")
        driver.quit()
        
    # 6. Save to CSV
    if scraped_garments:
        print(f"💾 Saving {len(scraped_garments)} garments to {output_filename}...")
        keys = scraped_garments[0].keys()
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(scraped_garments)
        print("✅ Data successfully saved! You did it.")

if __name__ == "__main__":
    target_url = "https://www.bewakoof.com/men-clothing"
    run_master_scraper(target_url, "final_bewakoof_20_tshirts.csv")