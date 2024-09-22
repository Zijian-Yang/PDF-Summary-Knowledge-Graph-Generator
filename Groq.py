# Groq.py
# This script generates summaries from text content using the Groq API with the llama3.1-70b model.
# It reads a text file, sends the content to Groq for summarization, and saves the result.

# Required packages:
# pip install groq python-dotenv

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve settings from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")
PROMPT_TEMPLATE = os.getenv("PROMPT_TEMPLATE")
INPUT_TEXT_FILE = "pdf_to_text_temp.txt"  
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_SUMMARY_LANGUAGE")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE"))
DEFAULT_MAX_TOKENS = min(int(os.getenv("DEFAULT_MAX_TOKENS", "4000")), 8000)

# Create Groq client
client = Groq(api_key=GROQ_API_KEY)

def read_text_content(file_path):
    """
    Read the content of a text file.
    
    Args:
    file_path (str): Path to the text file.
    
    Returns:
    str: Content of the text file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_summary(content):
    """
    Generate a summary using the Groq API.
    
    Args:
    content (str): The text content to summarize.
    
    Returns:
    str: The generated summary.
    
    Raises:
    Exception: If there's an error in the API call.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": PROMPT_TEMPLATE.format(language=DEFAULT_LANGUAGE, content=content)}
    ]
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

def save_summary(summary, output_file):
    """
    Save the generated summary to a file.
    
    Args:
    summary (str): The summary to save.
    output_file (str): Path to the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(summary)

def main():
    # Read text content
    text_content = read_text_content(INPUT_TEXT_FILE)
    
    # Generate summary
    summary = generate_summary(text_content)
    
    # Save summary
    save_summary(summary, OUTPUT_FILE)
    
    print(f"Summary generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
