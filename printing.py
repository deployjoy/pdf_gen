import os
import time
import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def convert_html_to_pdf(html_file_path, output_pdf_path, timeout=120):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")  # Disable CORS checks
    chrome_options.add_argument("--allow-file-access-from-files")  # Allow file:// access
    chrome_options.add_experimental_option('prefs', {
        "printing.print_preview_sticky_settings.appState": json.dumps({
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        })
    })

    service = Service('/home/zanad/chromedriver-linux64/chromedriver')  # Update this path

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Get the directory of the HTML file
        base_dir = os.path.dirname(os.path.abspath(html_file_path))
        file_url = f"file://{os.path.abspath(html_file_path)}"
        
        driver.get(file_url)

        print("Page loaded. Waiting for content to render...")

        # Wait for body content to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Inject CSS directly into the page
        css_file_path = os.path.join(base_dir, "style.css")
        if os.path.exists(css_file_path):
            with open(css_file_path, 'r') as css_file:
                css_content = css_file.read()
            driver.execute_script(f"var style = document.createElement('style'); style.textContent = '{css_content}'; document.head.appendChild(style);")
            print("CSS injected directly into the page.")
        else:
            print("CSS file not found.")

        # Check if Paged.js is loaded
        is_pagedjs_loaded = driver.execute_script("return typeof Paged !== 'undefined'")
        print(f"Is Paged.js loaded: {is_pagedjs_loaded}")

        if is_pagedjs_loaded:
            print(f"Waiting up to {timeout} seconds for Paged.js to finish...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                is_finished = driver.execute_script("""
                    return document.querySelector('.pagedjs_pages') !== null;
                """)
                if is_finished:
                    print("Paged.js finished rendering.")
                    break
                time.sleep(1)
            else:
                print("Paged.js rendering timed out. Proceeding with PDF generation.")
        else:
            print("Paged.js not detected. Waiting for general page load...")
            time.sleep(5)  # Adjust this time as needed

        # Print page dimensions
        page_width = driver.execute_script("return document.body.scrollWidth")
        page_height = driver.execute_script("return document.body.scrollHeight")
        print(f"Page dimensions: {page_width}x{page_height}")

        # Take a screenshot for debugging
        driver.save_screenshot("debug_screenshot.png")
        print("Debug screenshot saved as debug_screenshot.png")

        # Print any console errors
        console_logs = driver.get_log('browser')
        if console_logs:
            print("Console errors:")
            for log in console_logs:
                print(log)
        else:
            print("No console errors detected.")

        print("Generating PDF...")

        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
            'scale': 1,
        }
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)

        pdf_data = base64.b64decode(result['data'])

        with open(output_pdf_path, "wb") as f:
            f.write(pdf_data)

        print(f"PDF created successfully: {output_pdf_path}")
        print(f"PDF size: {len(pdf_data)} bytes")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

    finally:
        driver.quit()

# Usage
html_file_path = "index.html"
output_pdf_path = "output.pdf"
convert_html_to_pdf(html_file_path, output_pdf_path, timeout=120)