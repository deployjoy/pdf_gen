import asyncio
from pyppeteer import launch

async def print_webpage_to_pdf(url, output_file):
    # Launch the browser
    browser = await launch()
    
    try:
        # Create a new page
        page = await browser.newPage()
        
        # Navigate to the specified URL
        await page.goto(url, {'waitUntil': 'networkidle0'})
        
        # Generate PDF
        await page.pdf({'path': output_file, 'format': 'A4'})
        
        print(f"PDF saved as {output_file}")
    
    finally:
        # Close the browser
        await browser.close()

# URL of the webpage to convert
url = "https://deployjoy.github.io/pdf_gen/"

# Output PDF file name
output_file = "webpage.pdf"

# Run the async function
asyncio.get_event_loop().run_until_complete(print_webpage_to_pdf(url, output_file))