# ReferenceGenerator.py
# This script extracts arXiv IDs from a text file, generates citations, and appends them to an output file.
# Required libraries: arxiv, datetime, re, os

import arxiv
import datetime
import re
import os

# Extract arXiv ID from text using regex
def extract_arxiv_id(text):
    pattern = r'arXiv:(\d{4}\.\d{5}v\d+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

# Generate citation for a given arXiv ID
def get_arxiv_citation(arxiv_id):
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results())
    
    authors = ", ".join([author.name for author in paper.authors])
    year = paper.published.year
    
    citation = f"{authors}. ({year}). {paper.title}. ArXiv.org. https://arxiv.org/abs/{arxiv_id}"
    
    return citation

# Append citation to the output file
def append_citation_to_output(citation):
    with open('output.txt', 'a', encoding='utf-8') as file:
        file.write('\n\n')  # Add two newlines to create a blank line
        file.write(citation)

# Read the pdf_to_text_temp.txt file
with open('pdf_to_text_temp.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Extract arXiv ID from the file content
arxiv_id = extract_arxiv_id(content)

if arxiv_id:
    # Generate citation using the extracted arXiv ID
    citation = get_arxiv_citation(arxiv_id)
    print("Generated citation:")
    print(citation)
    
    # Append the citation to the output.txt file
    append_citation_to_output(citation)
    print("Citation has been added to the end of output.txt")
else:
    print("No valid arXiv ID found")
