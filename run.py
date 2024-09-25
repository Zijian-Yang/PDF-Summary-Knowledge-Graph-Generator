import subprocess
import time
import sys

def run_script(script_name):
    try:
        process = subprocess.Popen(['python3', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        success = False
        try:
            output, error = process.communicate(timeout=25)  # Set timeout threshold to 25 seconds
        except subprocess.TimeoutExpired:
            process.kill()
            output, error = process.communicate()
            print(f"{script_name} terminated due to timeout", file=sys.stderr)
            return success

        if output:
            print(output.strip())
            if script_name == 'PDFParser.py' and 'PDF content has been extracted to pdf_to_text_temp.txt' in output:
                success = True
            elif script_name == 'Groq.py' and 'Summary generated and saved to output.txt' in output:
                success = True
            elif script_name == 'GraphMaker2_png.py' and 'Knowledge graph has been generated and saved as' in output:
                success = True
        if error:
            print(f"Error: {error.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"An exception occurred while running {script_name}: {e}", file=sys.stderr)
    return success

def main():
    scripts = ['PDFParser.py', 'Groq.py', 'GraphMaker2_png.py']
    
    for i, script in enumerate(scripts):
        print(f"Running {script}...")
        max_retries = 3 if i < len(scripts) - 1 else 1  # Only try once for the last script
        for attempt in range(max_retries):
            if run_script(script):
                print(f"{script} execution successful\n")
                break
            else:
                if attempt < max_retries - 1:
                    print(f"{script} failed to complete the expected task, retrying... (Attempt {attempt + 2}/{max_retries})")
                    time.sleep(5)  # Increase wait time
                elif script == 'GraphMaker2_png.py':
                    print(f"{script} execution completed, but success message not detected. Continuing execution.\n")
                else:
                    print(f"{script} failed to complete successfully after {max_retries} attempts. Skipping this script.\n")
                    return  # Stop executing subsequent tasks if one task fails

if __name__ == "__main__":
    main()

# For the last script, we don't need to detect success, just wait for it to finish.