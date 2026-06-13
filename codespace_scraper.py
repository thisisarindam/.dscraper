from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def scrape_bewakoof_20_items(url, output_filename):
    print("🚀 Booting up Headless Chrome for Bewakoof...")
    
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
        
        print("Checking for subscription alert...")
        try:
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[self::button or self::span or self::a][normalize-space()='NO' or normalize-space()='No']"))
            )
            no_button.click()
            print("Closed subscription alert by clicking 'NO'.")
            time.sleep(1)
        except Exception:
            print("No subscription alert detected.")
        
        print("Attempting to click the 'Sort By' menu...")
        try:
            sort_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'SORT BY', 'sort by'), 'sort by')] | //div[contains(@class, 'sort-')]"))
            )
            sort_button.click()
            time.sleep(1) 
            
            new_arrival_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'New') or contains(text(), 'new')]"))
            )
            new_arrival_option.click()
            print("Selected 'New Arrivals'. Waiting for grid to refresh...")
            time.sleep(4) 
            
        except Exception as sort_error:
            print("⚠️ Could not click the sort buttons. Continuing with default layout...")
        
        # INCREASED SCROLLING: Changed from 6 to 8 scrolls to ensure 20 items load
        print("Scrolling down to force high-res images to load...")
        for i in range(8):
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(2.5) 
            
        print("Locating garments...")
        products = driver.find_elements(By.CSS_SELECTOR, "section[data-testid^='product-card-']")
        
        # INCREASED LIMIT: Changed from 15 to 20
        print(f"Found {len(products)} product cards on screen. Extracting exactly 20...")
        
        for index, product in enumerate(products[:20]):
            try:
                # Extract Image URL
                image_element = product.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("src")
                if not image_url or "placeholder" in image_url.lower() or image_url.startswith("data:image"):
                    image_url = image_element.get_attribute("data-src") or image_url

                # Extract Title
                try:
                    title_element = product.find_element(By.CSS_SELECTOR, "[data-testid='product-title']")
                    title = title_element.text.strip()
                except Exception:
                    title = "Title not found"

                # Extract Price
                try:
                    price_elements = product.find_elements(By.XPATH, ".//*[contains(text(), '₹')]")
                    price = price_elements[0].text.strip() if price_elements else "Price not found"
                except Exception:
                    price = "Price not found"
                
                print(f"Extracted {index + 1}/20: {title} | {price}")
                
                scraped_garments.append({
                    "Title": title,
                    "Price": price,
                    "Image_URL": image_url
                })
                
            except Exception as e:
                print(f"⚠️ Skipped item {index + 1}: Data missing. ({e})")

    except Exception as e:
        print(f"❌ Critical Error! {e}")
        
    finally:
        print("Closing browser...")
        driver.quit()
        
    if scraped_garments:
        print(f"💾 Saving {len(scraped_garments)} garments to {output_filename}...")
        keys = scraped_garments[0].keys()
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(scraped_garments)
        print("✅ Data successfully saved!")

if __name__ == "__main__":
    target_url = "https://www.bewakoof.com/men-clothing"
    scrape_bewakoof_20_items(target_url, "bewakoof_top_20_new.csv")