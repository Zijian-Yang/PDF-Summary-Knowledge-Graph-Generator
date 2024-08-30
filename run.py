import os
from dotenv import load_dotenv
import PDFParser
import Ollama
import GraphMaker

# 加载.env文件
load_dotenv()

def main():
    # 步骤1：运行PDFParser
    print("正在运行PDFParser...")
    PDFParser.main()
    
    # 步骤2：运行Ollama
    print("正在运行Ollama...")
    Ollama.main()
    
    # 步骤3：运行GraphMaker
    print("正在运行GraphMaker...")
    GraphMaker.main()
    
    # 步骤4：删除临时文件
    temp_file = 'pdf_to_text_temp.txt'
    try:
        os.remove(temp_file)
        print(f"临时文件 {temp_file} 已删除")
    except OSError as e:
        print(f"删除临时文件时出错: {e}")

if __name__ == "__main__":
    main()
