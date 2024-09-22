# PDFParser.py
# This script converts a PDF file to text, extracting its content while removing references.
# It uses PyMuPDF to convert PDF to HTML, then BeautifulSoup to parse the HTML and extract text.
# The process involves creating a temporary HTML file which is deleted after text extraction.

# Required libraries:
# pip install PyMuPDF beautifulsoup4 tqdm python-dotenv requests

import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Read configurations from the .env file
INPUT_PDF_PATH = os.getenv('INPUT_PDF_PATH', 'input.pdf')
HTML_PATH = 'temp.html'
OUTPUT_TXT_PATH = 'pdf_to_text_temp.txt'

# Convert PDF to HTML
def pdf2html(input_path, html_path):
    with fitz.open(input_path) as doc:
        html_content = ''.join(page.get_text('html') for page in tqdm(doc))
    html_content += "</body></html>"
    with open(html_path, 'w', encoding='utf-8', newline='') as fp:
        fp.write(html_content)

# Parse local HTML using BeautifulSoup and extract text
def html2txt(html_path, output_path):
    with open(html_path, 'r', encoding='utf-8') as html_file, open(output_path, 'w', encoding='utf-8') as text_file:
        soup = BeautifulSoup(html_file, "html.parser")
        for div in soup.find_all('div'):
            for p in div.children:
                if isinstance(p, str):
                    text = p.strip()
                else:
                    text = ''.join(span.text for span in p.find_all('span') if span.text)
                if text:
                    if "References" in text:
                        return  # Stop processing when "References" is encountered
                    text_file.write(text + '\n')

# Delete the temporary HTML file
def delete_html_file(html_path):
    try:
        os.remove(html_path)
        print(f"Temporary HTML file {html_path} has been deleted")
    except OSError as e:
        print(f"Error occurred while deleting the file: {e}")

# Main function
def main():
    pdf2html(INPUT_PDF_PATH, HTML_PATH)
    html2txt(HTML_PATH, OUTPUT_TXT_PATH)
    delete_html_file(HTML_PATH)
    print(f"PDF content has been extracted to {OUTPUT_TXT_PATH}")

if __name__ == "__main__":
    main()