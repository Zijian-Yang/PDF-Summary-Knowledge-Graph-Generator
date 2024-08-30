# pip install langchain langchain-community graphviz knowledge-graph-maker
import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from knowledge_graph_maker import GraphMaker, Ontology, Document
import graphviz
import textwrap

# 加载.env文件
load_dotenv()

# 从.env文件中读取配置
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL')
GRAPH_WIDTH = os.getenv('GRAPH_WIDTH', '16.67')
GRAPH_HEIGHT = os.getenv('GRAPH_HEIGHT', '8.71')
GRAPH_DPI = os.getenv('GRAPH_DPI', '72')
NODE_FONT = os.getenv('NODE_FONT', 'Arial')
NODE_WIDTH = os.getenv('NODE_WIDTH', '2')
NODE_HEIGHT = os.getenv('NODE_HEIGHT', '0.7')
EDGE_FONT = os.getenv('EDGE_FONT', 'Arial')
MAX_EDGES = int(os.getenv('MAX_EDGES', '15'))

# 定义本体
ontology = Ontology(
    labels=[
        "Technology",
        "Method",
        "Problem",
        "Result",
    ],
    relationships=[
        "solves",
        "implements",
        "improves",
        "achieves",
    ]
)

# 创建Ollama LLM客户端
class OllamaClient:
    def __init__(self, model=DEFAULT_MODEL):
        self.llm = Ollama(base_url='http://localhost:11434', model=model)
    
    def generate(self, user_message, system_message="", **kwargs):
        prompt = f"{system_message}\n\n{user_message}" if system_message else user_message
        return self.llm(prompt)

llm_client = OllamaClient()

# 创建GraphMaker实例
graph_maker = GraphMaker(ontology=ontology, llm_client=llm_client, verbose=True)

# 读取并处理文本文件
def process_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # 使用LangChain的文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    
    return [Document(text=chunk, metadata={"source": file_path}) for chunk in chunks]

# 生成图谱
documents = process_text_file("output.txt")
graph = graph_maker.from_documents(documents)

# 使用Graphviz创建可视化图谱
dot = graphviz.Digraph(comment='Knowledge Graph', format='png')
dot.attr(rankdir='LR', size=f'{GRAPH_WIDTH},{GRAPH_HEIGHT}', dpi=GRAPH_DPI)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue', fontname=NODE_FONT, width=NODE_WIDTH, height=NODE_HEIGHT)
dot.attr('edge', fontname=EDGE_FONT)

# 添加节点和边，限制节点数量
added_nodes = set()
for edge in graph[:MAX_EDGES]:
    node1_label = '\n'.join(textwrap.wrap(edge.node_1.name, width=20))
    node2_label = '\n'.join(textwrap.wrap(edge.node_2.name, width=20))
    if edge.node_1.name not in added_nodes:
        dot.node(edge.node_1.name, node1_label)
        added_nodes.add(edge.node_1.name)
    if edge.node_2.name not in added_nodes:
        dot.node(edge.node_2.name, node2_label)
        added_nodes.add(edge.node_2.name)
    dot.edge(edge.node_1.name, edge.node_2.name, label=edge.relationship)

# 保存为PNG文件
dot.render("knowledge_graph", cleanup=True)
print("知识图谱已生成为knowledge_graph.png")