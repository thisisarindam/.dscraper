from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re

def scrape_rare_rabbit():
    print("🚀 Booting up Headless Chrome for Rare Rabbit...")
    
    # --- Cloud Configurations ---
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
    actions = ActionChains(driver) # Initialize the virtual mouse
    scraped_garments = []
    
    try:
        # Step 1: Open URL
        target_url = "https://thehouseofrare.com/pages/rare-rabbit"
        print(f"Step 1: Navigating to {target_url}")
        driver.get(target_url)
        
        # Step 2: Wait for a few seconds
        print("Step 2: Waiting for the initial page load...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3) 

        # Step 3 & 4: Hover over "MEN"
        print("Step 3: Attempting to hover over the 'MEN' section...")
        try:
            # Look for the MEN navigation link (broad XPath to catch variations)
            men_menu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//nav//a[contains(translate(text(), 'MEN', 'men'), 'men')] | //header//span[contains(translate(text(), 'MEN', 'men'), 'men')]"))
            )
            # Simulate mouse hover
            actions.move_to_element(men_menu).perform()
            time.sleep(2) # Wait for dropdown animation
            
            # Step 5: Click "NEW IN"
            print("Step 5: Clicking 'NEW IN' from the dropdown...")
            new_in_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(text(), 'NEW IN', 'new in'), 'new in')]"))
            )
            driver.execute_script("arguments[0].click();", new_in_link)
            print("Navigating to New Arrivals grid...")
            time.sleep(5)
            
        except Exception as e:
            print("⚠️ Could not perform hover navigation. Taking screenshot 'rare_hover_error.png'...")
            driver.save_screenshot("rare_hover_error.png")
            print("Attempting to bypass by going to assumed direct URL...")
            driver.get("https://thehouseofrare.com/collections/new-arrivals-men")
            time.sleep(5)

        # Step 6: Filter > Category > T-SHIRT
        print("Step 6: Attempting to apply 'T-SHIRT' category filter...")
        try:
            # 6a. Try to click a generic 'Filter' button if it exists and hides the sidebar
            try:
                filter_btn = driver.find_element(By.XPATH, "//*[self::button or self::span][contains(translate(text(), 'FILTER', 'filter'), 'filter')]")
                driver.execute_script("arguments[0].click();", filter_btn)
                time.sleep(1)
            except:
                pass # Filters might already be visible on desktop view

            # 6b. Try to open 'Category' accordion
            try:
                category_header = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'CATEGORY', 'category'), 'category')]")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category_header)
                driver.execute_script("arguments[0].click();", category_header)
                time.sleep(1)
            except:
                pass # Might already be open
            
            # 6c. Click the T-Shirt checkbox/label
            tshirt_filter = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//label[contains(translate(., 'T-SHIRT', 't-shirt'), 't-shirt')] | //a[contains(translate(., 'T-SHIRT', 't-shirt'), 't-shirt')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tshirt_filter)
            driver.execute_script("arguments[0].click();", tshirt_filter)
            print("T-Shirt filter applied. Waiting for grid refresh...")
            time.sleep(4)
            
        except Exception as filter_error:
            print(f"⚠️ Could not apply T-Shirt filter: {filter_error}")
            driver.save_screenshot("rare_filter_error.png")

        # Step 7: Scroll down 5 times and wait for 30 seconds
        print("Step 7: Scrolling 5 times to load images (30-second duration)...")
        for i in range(5):
            driver.execute_script("window.scrollBy(0, 900);")
            print(f"  - Scroll {i+1}/5 complete. Waiting 6 seconds...")
            time.sleep(6) # 5 loops * 6 seconds = 30 seconds total waiting
            
        # Step 8: Scroll up to the upper section
        print("Step 8: Scrolling back to the top of the product area...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Step 9: Extract product image URLs only
        print("Step 9: Collecting product image URLs...")

        image_candidates = driver.find_elements(By.XPATH, "//a[contains(@href, '/products/') or contains(@href, '/collections/')]//img | //article[contains(@class, 'product') or contains(@class, 'card') or contains(@class, 'item')][.//img]//img")

        if not image_candidates:
            image_candidates = driver.find_elements(By.XPATH, "//img[contains(@src, 'cdn') or contains(@data-src, 'cdn') or contains(@srcset, 'cdn')]")

        unique_images = set()
        for img in image_candidates:
            try:
                srcset = img.get_attribute("data-srcset") or img.get_attribute("srcset")
                if srcset:
                    image_url = srcset.split(",")[-1].strip().split(" ")[0]
                else:
                    image_url = img.get_attribute("data-src") or img.get_attribute("src")

                if image_url:
                    image_url = image_url.split("?")[0]
                    image_url = re.sub(r'_\d+x\d*', '', image_url)
                    image_url = re.sub(r'_crop_[a-z]+', '', image_url)
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

                if image_url and not any(x in image_url.lower() for x in ("placeholder", "data:image")):
                    unique_images.add(image_url)
            except Exception:
                continue

        for index, image_url in enumerate(list(unique_images)[:30], start=1):
            scraped_garments.append({"Image_URL": image_url})
            print(f"Extracted {index}/30 image URL")

        print(f"Collected {len(scraped_garments)} product images.")

    except Exception as e:
        print(f"❌ Critical Error during execution! {e}")
        driver.save_screenshot("rare_rabbit_crash.png")
        
    finally:
        print("Closing browser...")
        driver.quit()
        
    # Step 10: Save only image URLs to CSV
    if scraped_garments:
        output_filename = "rare_rabbit_30_tshirts.csv"
        print(f"Step 10: 💾 Saving {len(scraped_garments)} image URLs to {output_filename}...")
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=["Image_URL"])
            dict_writer.writeheader()
            dict_writer.writerows(scraped_garments)
        print("✅ Image URLs successfully saved!")

if __name__ == "__main__":
    scrape_rare_rabbit()