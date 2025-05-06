from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def setup_driver():
    options = Options()
    options.add_argument("--headless")  # comment this out if you want to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(options=options)


# def safe_get(driver, by, value):
#     try:
#         return driver.find_element(by, value).text.strip()
#     except:
#         return None

def safe_get(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element.text.strip()
    except:
        return None



# def scrape_amazon_product_selenium(url):
#     driver = setup_driver()
#     driver.get(url)
#     time.sleep(3)

#     product = {
#         "title": safe_get(driver, By.ID, "productTitle"),
#         "price": safe_get(driver, By.CLASS_NAME, "a-price-whole"),
#         "description": safe_get(driver, By.ID, "feature-bullets"),
#         "manufacturer": safe_get(driver, By.ID, "bylineInfo"),
#         "rating": safe_get(driver, By.CLASS_NAME, "a-icon-alt")
#     }

def scrape_amazon_product_selenium(url):
    driver = setup_driver()
    driver.get(url)

    try:
        product = {
            "title": safe_get(driver, By.ID, "productTitle"),
            "price": (
                safe_get(driver, By.CLASS_NAME, "a-price-whole")
                or safe_get(driver, By.CSS_SELECTOR, ".a-price .a-offscreen")
            ),
            "description": safe_get(driver, By.ID, "feature-bullets"),
            "manufacturer": safe_get(driver, By.ID, "bylineInfo"),
            "rating": safe_get(driver, By.CLASS_NAME, "a-icon-alt"),
        }
    except Exception as e:
        product = {"error": f"Amazon scraping error: {str(e)}"}

    driver.quit()
    return product



    driver.quit()
    return product


def scrape_flipkart_product_selenium(url):
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)

    try:
        try:
            close_button = driver.find_element(By.XPATH, "//button[contains(text(), '✕')]")
            close_button.click()
            time.sleep(1)
        except:
            pass

        title = safe_get(driver, By.CLASS_NAME, 'B_NuCI')
        price = safe_get(driver, By.CLASS_NAME, '_30jeq3')

        desc_blocks = driver.find_elements(By.CLASS_NAME, '_1mXcCf')
        if not desc_blocks:
            desc_blocks = driver.find_elements(By.CLASS_NAME, '_3la3Fn')

        description = "\n".join([block.text for block in desc_blocks if block.text.strip()]) or "Description not available"

        specs = driver.find_elements(By.CLASS_NAME, '_21lJbe')
        manufacturer = specs[0].text if specs else "N/A"

        rating = safe_get(driver, By.CLASS_NAME, '_3LWZlK')

        product = {
            "title": title or "N/A",
            "price": price.replace('₹', '').replace(',', '') if price else "N/A",
            "description": description,
            "manufacturer": manufacturer,
            "rating": rating or "N/A"
        }
    except Exception as e:
        product = {"error": f"Failed to scrape Flipkart product: {str(e)}"}

    driver.quit()
    return product


def get_amazon_alternatives(query):
    driver = setup_driver()
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)

    alternatives = []
    results = driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item")[:5]

    for item in results:
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")
            try:
                price = item.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
            except:
                price = "N/A"
            alternatives.append({"title": title, "url": link, "price": price})
        except:
            continue

    driver.quit()
    return alternatives

# Alias for compatibility with import name used in app.py
search_amazon_alternatives = get_amazon_alternatives





