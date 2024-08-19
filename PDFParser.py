# pip install PyMuPDF beautifulsoup4 tqdm

import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
import re


# 将pdf转成html
def pdf2html(input_path, html_path):
    doc = fitz.open(input_path)
    # print(doc)  # 注释掉，避免输出PDF文档对象
    html_content = ''
    for page in tqdm(doc):
        html_content += page.get_text('html')
    # print('开始输出html文件')  # 注释掉，避免输出提示信息
    html_content += "</body></html>"
    with open(html_path, 'w', encoding='utf-8', newline='') as fp:
        fp.write(html_content)


# 使用BeautifulSoup解析本地html
def html2txt(html_path):
    html_file = open(html_path, 'r', encoding='utf-8')
    htmlhandle = html_file.read()
    soup = BeautifulSoup(htmlhandle, "html.parser")

    references_found = False  # 用于标记是否找到"References"

    for div in soup.find_all('div'):
        for p in div:
            text = str()
            for span in p:
                p_info = '<span .*?>(.*?)</span>'  # 提取规则
                res = re.findall(p_info, str(span))  # findall函数
                if len(res) == 0:
                    pass
                else:
                    text += res[0]  # 将列表中的字符串内容合并加到行字符串中

            if "References" in text:
                references_found = True  # 找到"References"后停止处理
                break

            if not references_found:
                with open("pdf_to_text_temp.txt", 'a', encoding='utf-8') as text_file:
                    text_file.write(text)
                    text_file.write('\n')

        if references_found:
            break  # 找到"References"后停止处理整个文件


# 主函数
input_path = r'4.pdf'
html_path = r'pdf_to_html_temp.html'
pdf2html(input_path, html_path)  # pdf转html
html2txt(html_path)  # 解析html保存为txt
