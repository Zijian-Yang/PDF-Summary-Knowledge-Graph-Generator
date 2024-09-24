import subprocess
import time
import sys

def run_script(script_name):
    process = subprocess.Popen(['python3', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    success = False
    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output == '' and error == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            if script_name == 'PDFParser.py' and 'PDF content has been extracted to pdf_to_text_temp.txt' in output:
                success = True
            elif script_name == 'Groq.py' and 'Summary generated and saved to output.txt' in output:
                success = True
        if error:
            print(f"错误: {error.strip()}", file=sys.stderr)
    return success

def main():
    scripts = ['PDFParser.py', 'Groq.py', 'GraphMaker2_png.py']
    
    for script in scripts:
        print(f"正在运行 {script}...")
        max_retries = 3
        for attempt in range(max_retries):
            if run_script(script):
                print(f"{script} 运行成功\n")
                break
            else:
                if attempt < max_retries - 1:
                    print(f"{script} 未能完成预期任务,正在重试... (尝试 {attempt + 2}/{max_retries})")
                    time.sleep(5)  # 增加等待时间
                else:
                    print(f"{script} 在 {max_retries} 次尝试后仍未成功完成。跳过此脚本。\n")
                    return  # 如果一个任务失败，停止执行后续任务

if __name__ == "__main__":
    main()
