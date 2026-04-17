from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

host = "https://www.aida.de"

try:
    # Set up headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(host)

    # Check if the page loaded
    if "aida.de" in driver.title:
        print("✅ Page loaded successfully!")
    else:
        print("❌ Page did not load.")

    driver.quit()
except Exception as e:
    print(f"❌ Selenium test failed: {e}")