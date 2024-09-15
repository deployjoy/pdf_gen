# DeployJoy PDF Guide
### How to make a beautiful PDF from HTML.

This repo is a fork of https://github.com/ashok-khanna/pdf_gen you can read the original guide here: https://ashok-khanna.github.io/pdf/

The goal with this repo is to create a simple and quick workflow to generate professional, customised PDFs. 
This can be used for Proposals, SOA's, SOP's, really any professional document that needs to look great and be easy to maintain.

First Step is to define the style parameters in `style.css` these are the same parameters that can be used in the HTML to style the page.

You can then fill in the data in the html file `index.html` this is the content that will be displayed in the PDF.

You need to publish the HTML file to the web and then use the URL to generate the PDF, using the print_2.py script. 

### Next Steps
- Write a python script to generate the json file by querying a LLM.
- Build this into a more hands off workflow.
- Build this into a web app.


### INPUTS TO BE HARD CODED.
- Json Content File, AI can create this actually. But I need to provide a template to the AI. The content within the JSON needs to be in MD syntax.
- Formatting, text, backgrounds (canva .svg), colours, etc. All these are hardcoded in style.css. Later on when this becomes a web-app, these can be dynamic or selected in a UI.
- html template will change depending on the functionality required of the PDF. TOC, Automatic Numbers, Cover Page, Banners etc.

### Deployment
- Unless I clone the repo, I can only generate one pdf at a time. Becuase it is hosted on github pages.
- I should be able to just change the json file, then run a bash script that runs generate html, push to github, then run printing script to generate the pdf. I should make the printing script save the file in a google drive folder rather than locally.


# NEXT THING IS TO FOCUS ON GETTING GOOD CONTENT INTO THE JSON FILE.
- This means good prompts, good scraping, good inputs and parameters into the LLM. to generate valuable, professional content.