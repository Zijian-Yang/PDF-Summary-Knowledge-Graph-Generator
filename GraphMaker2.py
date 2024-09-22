import os
from dotenv import load_dotenv
from groq import Groq
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import json
from json import JSONDecodeError
import time
import json5

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

def read_paper_content(file_path='pdf_to_text_temp.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def normalize_json(json_str):
    try:
        # 使用 json5 解析 JSON 字符串
        data = json5.loads(json_str)
        # 重新序列化为标准 JSON
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"JSON parsing failed: {str(e)}")
        return None

def analyze_paper(content):
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = """
    As a professional academic paper analysis expert, please carefully analyze the following paper content and extract key concepts, methods, results, and conclusions.

    Please follow these guidelines:
    1. Identify the main research topics and key concepts
    2. Extract important methods or techniques used
    3. Summarize the main research findings and results
    4. Identify the paper's main conclusions and contributions
    5. Note any future research directions or challenges mentioned in the paper

    Please return a JSON-compliant object containing the following two lists:
    1. 'entities': Each entity includes 'id' (unique identifier) and 'label' (entity name or description)
    2. 'relations': Each relation includes 'source' (source entity id), 'target' (target entity id), and 'label' (relation description)

    Ensure that entities and relations accurately reflect the core content and structure of the paper. Try to use professional terminology from the paper, maintaining academic accuracy.
    Please use double quotes, correct commas and colons, and appropriate indentation.

    Paper content:
    {content}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing academic papers and extracting key information."},
                    {"role": "user", "content": prompt.format(content=content)}
                ]
            )
            
            result = response.choices[0].message.content
            print("API Response:", result)  # Print raw response
            
            # Attempt to normalize JSON
            normalized_result = normalize_json(result)
            if normalized_result:
                parsed_result = json.loads(normalized_result)
                return parsed_result
            else:
                # If normalization fails, try to have the model correct the JSON
                correction_prompt = f"Please correct the following non-standard JSON and return it in a standard format:\n{result}"
                correction_response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a JSON format expert."},
                        {"role": "user", "content": correction_prompt}
                    ]
                )
                corrected_result = correction_response.choices[0].message.content
                return json.loads(corrected_result)
        
        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                print("Maximum retry attempts reached. Returning empty result.")
                return {"entities": [], "relations": []}

def create_knowledge_graph(entities, relations):
    G = nx.Graph()
    
    for entity in entities:
        G.add_node(entity['id'], label=entity['label'])
    
    for relation in relations:
        G.add_edge(relation['source'], relation['target'], label=relation['label'])
    
    return G

def visualize_graph(G):
    net = Network(notebook=False, width="100%", height="600px", bgcolor="#222222", font_color="white")
    
    for node in G.nodes(data=True):
        net.add_node(node[0], label=node[1]['label'], title=node[1]['label'])
    
    for edge in G.edges(data=True):
        net.add_edge(edge[0], edge[1], title=edge[2].get('label', ''))
    
    net.save_graph("knowledge_graph.html")
    print("Knowledge graph has been generated and saved as 'knowledge_graph.html'.")

def main():
    content = read_paper_content()
    analysis_result = analyze_paper(content)
    
    if not isinstance(analysis_result, dict) or 'entities' not in analysis_result or 'relations' not in analysis_result:
        print("Error: Analysis result does not contain expected 'entities' and 'relations' keys.")
        print("API returned result:", analysis_result)
        return
    
    if not analysis_result['entities'] or not analysis_result['relations']:
        print("Warning: Entity or relation list is empty.")
        print("Entities:", analysis_result['entities'])
        print("Relations:", analysis_result['relations'])
    
    G = create_knowledge_graph(analysis_result['entities'], analysis_result['relations'])
    
    if G.number_of_nodes() == 0:
        print("Error: Generated graph has no nodes.")
        return
    
    visualize_graph(G)

if __name__ == "__main__":
    main()
