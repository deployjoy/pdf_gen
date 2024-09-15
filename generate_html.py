import json
from jinja2 import Environment, FileSystemLoader
import markdown


# Load content from a JSON file
def load_content(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def convert_markdown(content):
    if isinstance(content, str):
        return markdown.markdown(content)
    elif isinstance(content, dict):
        return {k: convert_markdown(v) for k, v in content.items()}
    elif isinstance(content, list):
        return [convert_markdown(item) for item in content]
    else:
        return content

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