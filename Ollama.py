# pip install requests
# if ollama is not running, run the following command:
# net stop winnat
# net start winnat

import os
import requests
import time
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def read_txt_file(file_path='pdf_to_text_temp.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_ollama_response(prompt, model, temperature, max_tokens):
    url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    max_retries = int(os.getenv('MAX_RETRIES', 3))
    retry_delay = int(os.getenv('RETRY_DELAY', 2))
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            print(f"请求错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("达到最大重试次数，放弃请求。")
                return None

def generate_summary(content, model, temperature, max_tokens, language):
    prompt_template = os.getenv('PROMPT_TEMPLATE')
    if not prompt_template:
        raise ValueError("PROMPT_TEMPLATE 未在 .env 文件中设置")
    
    prompt = prompt_template.format(language=language, content=content)
    
    return get_ollama_response(prompt, model, temperature, max_tokens)

def check_ollama_status():
    url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    try:
        response = requests.post(url, json={"model": "dummy", "prompt": "test"}, timeout=5)
        return response.status_code in [200, 404]
    except requests.exceptions.RequestException:
        return False

def main():
    if not check_ollama_status():
        print("警告：Ollama 似乎没有运行。请确保 Ollama 服务已启动。")
        return

    model = os.getenv('DEFAULT_MODEL')
    temperature = float(os.getenv('DEFAULT_TEMPERATURE'))
    max_tokens = int(os.getenv('DEFAULT_MAX_TOKENS'))
    language = os.getenv('DEFAULT_SUMMARY_LANGUAGE')

    if not all([model, temperature, max_tokens, language]):
        raise ValueError("缺少必要的环境变量设置。请检查 .env 文件。")

    content = read_txt_file()
    
    if not content:
        print("未找到内容或文件为空")
        return

    print("正在生成摘要...")
    summary = generate_summary(content, model, temperature, max_tokens, language)

    if summary:
        output_file = os.getenv('OUTPUT_FILE', 'output.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"摘要已保存到 {output_file}")
    else:
        print("生成摘要失败")

if __name__ == "__main__":
    main()