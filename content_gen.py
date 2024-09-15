import asyncio
from playwright.async_api import async_playwright
from jinja2 import Environment, FileSystemLoader
import os
import markdown
import base64
from bs4 import BeautifulSoup
import uuid

def b64encode_filter(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def read_svg(file_path):
    with open(file_path, 'r') as file:
        return file.read()

async def measure_element_heights(page, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'])
    
    # Assign unique IDs to elements
    for element in elements:
        element['id'] = str(uuid.uuid4())
    
    # Inject content into the page
    await page.set_content(str(soup))
    
    # Measure heights
    heights = await page.evaluate('''
        (ids) => {
            return ids.map(id => {
                const element = document.getElementById(id);
                if (element) {
                    return element.getBoundingClientRect().height;
                }
                return 0;
            });
        }
    ''', [element['id'] for element in elements])
    
    return list(zip(elements, heights))

async def split_content_into_pages(page, html_content, page_height, top_margin, bottom_margin):
    element_heights = await measure_element_heights(page, html_content)
    content_height = page_height - top_margin - bottom_margin
    pages = []
    current_page = []
    current_height = 0

    for element, height in element_heights:
        if current_height + height > content_height and current_page:
            pages.append(''.join(str(e) for e in current_page))
            current_page = []
            current_height = 0
        
        current_page.append(element)
        current_height += height

    if current_page:
        pages.append(''.join(str(e) for e in current_page))

    return pages

async def generate_pdf_from_markdown(markdown_file, template_file, output_file, context):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(script_dir))
    env.filters['b64encode'] = b64encode_filter
    template = env.get_template(template_file)

    # Read and convert markdown content
    with open(markdown_file, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()
    html_content = markdown.markdown(md_content, extensions=['extra'])

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set viewport size to A4
        page_width, page_height = 794, 1123
        await page.set_viewport_size({"width": page_width, "height": page_height})

        # Split content into pages
        top_margin, bottom_margin = 75, 113
        pages = await split_content_into_pages(page, html_content, page_height, top_margin, bottom_margin)

        # Add the HTML content to the context
        context['pages'] = pages

        # Render the template with the context
        full_html_content = template.render(context)

        await page.set_content(full_html_content)
        
        # Wait for any fonts or images to load
        await page.wait_for_load_state('networkidle')

        # Modify all links to open in a new tab
        await page.evaluate("""
            () => {
                const links = document.getElementsByTagName('a');
                for (let link of links) {
                    link.setAttribute('target', '_blank');
                }
            }
        """)

        # Generate PDF
        await page.pdf(path=output_file, format='A4', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        
        await browser.close()

    print(f"PDF generated successfully: {output_file}")

# Example usage
if __name__ == "__main__":
    context = {
        'title': 'Project Proposal',
        'background': read_svg('/home/zanad/documents/deployjoy-dev/deployjoy/projects/file_gen/src/file_gen/DeployJoy_proposal_footer.svg'),
    }
    
    asyncio.run(generate_pdf_from_markdown(
        markdown_file='/home/zanad/documents/deployjoy-dev/deployjoy/projects/file_gen/src/file_gen/Source_Financial_Proposal.md',
        template_file='content_template.html',
        output_file='Project_Proposal.pdf',
        context=context
    ))