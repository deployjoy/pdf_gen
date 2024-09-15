import json
from jinja2 import Environment, FileSystemLoader
import markdown
from markdown.extensions import Extension
from markdown.blockprocessors import ParagraphProcessor


# Load content from a JSON file
def load_content(filename):
    with open(filename, 'r') as file:
        return json.load(file)

class NoWrapParagraphProcessor(ParagraphProcessor):
    def run(self, parent, blocks):
        block = blocks.pop(0)
        if block.strip():
            parent.text = (parent.text or '') + '\n' + block

class NoWrapExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(NoWrapParagraphProcessor(md.parser), 'paragraph', 10)

def convert_markdown(content):
    if isinstance(content, str):
        return markdown.markdown(content, extensions=['extra', NoWrapExtension()])
    elif isinstance(content, dict):
        return {k: convert_markdown(v) for k, v in content.items()}
    elif isinstance(content, list):
        return [convert_markdown(item) for item in content]
    else:
        return content
    
# # Read and convert markdown content
# with open(markdown_file, 'r', encoding='utf-8') as md_file:
#     md_content = md_file.read()
# html_content = markdown.markdown(md_content, extensions=['extra'])

# Generate HTML using a template and content
def generate_html(template_file, content):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    content_html = convert_markdown(content)
    return template.render(content=content_html)

# Main function to orchestrate the HTML generation
def main():
    # Load content from a JSON file
    content = load_content('content_testing.json')
    
    # Generate HTML
    html = generate_html('dynamic_template.html', content)
    
    # Write the generated HTML to a file
    with open('index.html', 'w') as file:
        file.write(html)

if __name__ == "__main__":
    main()