# Ollama.py
# This script interacts with the Ollama API to generate summaries from text content.
# It reads a text file, sends the content to Ollama for summarization, and saves the result.
# The script also includes error handling, retries, and status checking for the Ollama service.

# Required packages:
# pip install requests python-dotenv

# Note: If Ollama is not running, execute the following commands:
# net stop winnat
# net start winnat

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_txt_file(file_path='pdf_to_text_temp.txt'):
    """
    Read the content of a text file.
    
    Args:
    file_path (str): Path to the text file. Defaults to 'pdf_to_text_temp.txt'.
    
    Returns:
    str: Content of the text file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_ollama_response(prompt, model, temperature, max_tokens):
    """
    Send a request to the Ollama API and get the response.
    
    Args:
    prompt (str): The input prompt for the model.
    model (str): The name of the model to use.
    temperature (float): The temperature setting for text generation.
    max_tokens (int): The maximum number of tokens to generate.
    
    Returns:
    str: The generated response from Ollama, or None if the request fails.
    """
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
            print(f"Request error (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("Maximum retry attempts reached. Abandoning request.")
                return None

def generate_summary(content, model, temperature, max_tokens, language):
    """
    Generate a summary using the Ollama API.
    
    Args:
    content (str): The text content to summarize.
    model (str): The name of the model to use.
    temperature (float): The temperature setting for text generation.
    max_tokens (int): The maximum number of tokens to generate.
    language (str): The language for the summary.
    
    Returns:
    str: The generated summary.
    """
    prompt_template = os.getenv('PROMPT_TEMPLATE')
    if not prompt_template:
        raise ValueError("PROMPT_TEMPLATE is not set in the .env file")
    
    prompt = prompt_template.format(language=language, content=content)
    
    return get_ollama_response(prompt, model, temperature, max_tokens)

def check_ollama_status():
    """
    Check if the Ollama service is running.
    
    Returns:
    bool: True if Ollama is running, False otherwise.
    """
    url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    try:
        response = requests.post(url, json={"model": "dummy", "prompt": "test"}, timeout=5)
        return response.status_code in [200, 404]
    except requests.exceptions.RequestException:
        return False

def main():
    """
    Main function to orchestrate the summarization process.
    """
    if not check_ollama_status():
        print("Warning: Ollama doesn't seem to be running. Please ensure the Ollama service is started.")
        return

    model = os.getenv('DEFAULT_MODEL')
    temperature = float(os.getenv('DEFAULT_TEMPERATURE'))
    max_tokens = int(os.getenv('DEFAULT_MAX_TOKENS'))
    language = os.getenv('DEFAULT_SUMMARY_LANGUAGE')

    if not all([model, temperature, max_tokens, language]):
        raise ValueError("Missing required environment variable settings. Please check the .env file.")

    content = read_txt_file()
    
    if not content:
        print("No content found or file is empty")
        return

    print("Generating summary...")
    summary = generate_summary(content, model, temperature, max_tokens, language)

    if summary:
        output_file = os.getenv('OUTPUT_FILE', 'output.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary has been saved to {output_file}")
    else:
        print("Failed to generate summary")

if __name__ == "__main__":
    main()