# pip install PyMuPDF beautifulsoup4 tqdm python-dotenv requests

import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 从.env文件中读取配置
INPUT_PDF_PATH = os.getenv('INPUT_PDF_PATH', 'input.pdf')
HTML_PATH = 'temp.html'
OUTPUT_TXT_PATH = 'pdf_to_text_temp.txt'

# 将pdf转成html
def pdf2html(input_path, html_path):
    with fitz.open(input_path) as doc:
        html_content = ''.join(page.get_text('html') for page in tqdm(doc))
    html_content += "</body></html>"
    with open(html_path, 'w', encoding='utf-8', newline='') as fp:
        fp.write(html_content)

# 使用BeautifulSoup解析本地html
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
                        return
                    text_file.write(text + '\n')

# 删除HTML文件
def delete_html_file(html_path):
    try:
        os.remove(html_path)
        print(f"临时HTML文件 {html_path} 已删除")
    except OSError as e:
        print(f"删除文件时出错: {e}")

# 主函数
def main():
    pdf2html(INPUT_PDF_PATH, HTML_PATH)
    html2txt(HTML_PATH, OUTPUT_TXT_PATH)
    delete_html_file(HTML_PATH)
    print(f"PDF内容已提取到 {OUTPUT_TXT_PATH}")

if __name__ == "__main__":
    main()