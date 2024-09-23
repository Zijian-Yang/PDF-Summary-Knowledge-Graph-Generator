import os
import re
from dotenv import load_dotenv
from groq import Groq
import networkx as nx
from pyvis.network import Network
import json
import time

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

def read_paper_content(file_path='pdf_to_text_temp.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_json_from_text(text):
    # Remove possible Markdown code block markers
    text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text, flags=re.MULTILINE)
    
    # Try to parse the entire text directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # If direct parsing fails, try to find JSON object
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None

def analyze_paper(content):
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = """
    As a professional academic paper analysis expert, please carefully analyze the following paper content and extract key concepts, methods, results, and conclusions.

    Please follow these guidelines:
    1. Identify the main research topics and key concepts (no more than 5-7 main entities)
    2. Extract important methods or techniques used
    3. Summarize the main research findings and results
    4. Identify the paper's main conclusions and contributions
    5. Note any future research directions or challenges mentioned in the paper

    Please return a JSON-compliant object containing the following two lists:
    1. 'entities': Each entity includes 'id' (unique identifier), 'label' (entity name or description), and 'importance' (a value from 1 to 5, where 5 is most important)
    2. 'relations': Each relation includes 'source' (source entity id), 'target' (target entity id), and 'label' (relation description)

    Ensure that entities and relations accurately reflect the core content and structure of the paper. Focus on the most important concepts and their relationships. Try to use professional terminology from the paper, maintaining academic accuracy.

    Return only the JSON object without any additional text, explanation, or code block markers.

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
            print(f"API Response (Attempt {attempt + 1}):")
            print(result)  # Print raw response
            
            # Extract and parse JSON from the response
            parsed_result = extract_json_from_text(result)
            if parsed_result and 'entities' in parsed_result and 'relations' in parsed_result:
                return parsed_result
            
            print(f"Failed to parse JSON on attempt {attempt + 1}")
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
            time.sleep(2)
    
    print("Maximum retry attempts reached. Returning empty result.")
    return {"entities": [], "relations": []}

def create_knowledge_graph(entities, relations):
    G = nx.Graph()
    
    for entity in entities:
        G.add_node(entity['id'], label=entity['label'], importance=entity['importance'])
    
    for relation in relations:
        G.add_edge(relation['source'], relation['target'], label=relation['label'])
    
    return G

def visualize_graph(G):
    net = Network(notebook=False, width="100%", height="600px", bgcolor="#222222", font_color="white")
    
    # Calculate node sizes based on importance
    max_importance = max(data['importance'] for _, data in G.nodes(data=True))
    min_importance = min(data['importance'] for _, data in G.nodes(data=True))
    
    for node, data in G.nodes(data=True):
        size = 20 + (data['importance'] - min_importance) / (max_importance - min_importance) * 30
        net.add_node(node, label=data['label'], title=data['label'], size=size)
    
    for edge in G.edges(data=True):
        net.add_edge(edge[0], edge[1], title=edge[2].get('label', ''))
    
    # Use physics layout for better positioning
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)
    
    net.save_graph("knowledge_graph.html")
    print("Knowledge graph has been generated and saved as 'knowledge_graph.html'.")

def main():
    content = read_paper_content()
    analysis_result = analyze_paper(content)
    
    if not analysis_result['entities'] or not analysis_result['relations']:
        print("Warning: Entity or relation list is empty.")
        print("Entities:", analysis_result['entities'])
        print("Relations:", analysis_result['relations'])
        return
    
    G = create_knowledge_graph(analysis_result['entities'], analysis_result['relations'])
    
    if G.number_of_nodes() == 0:
        print("Error: Generated graph has no nodes.")
        return
    
    visualize_graph(G)

if __name__ == "__main__":
    main()
