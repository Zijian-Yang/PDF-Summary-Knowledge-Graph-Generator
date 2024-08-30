# PDF-Summary-Knowledge-Graph-Generator

## Usage Steps

1. Start Ollama `ollama serve`
2. Install dependencies

```bash
pip install PyMuPDF beautifulsoup4 tqdm python-dotenv requests langchain langchain-community graphviz knowledge-graph-maker
```

2. Configure the `.env` file
3. Run `PDFParser.py` to convert pdf to txt
4. Run `Ollama.py` to generate summary file `output.txt`
5. Run `GraphMaker.py` to generate knowledge graph `knowledge_graph.png`

## Introduction

This project is a comprehensive tool designed to extract information from PDF documents, generate summaries, and create visual knowledge graphs. It leverages advanced natural language processing techniques and large language models to process and analyze academic papers or other complex documents.

## Core Components and Principles

1. PDF Parsing (PDFParser.py)

- Utilizes PyMuPDF to convert PDF files into HTML format.
- Employs BeautifulSoup to extract clean text from the HTML, focusing on relevant content and excluding references.
- Outputs a temporary text file for further processing.

2. Text Summarization (Ollama.py)

- Integrates with Ollama, a local large language model server.
- Sends the extracted text to the Ollama API for summarization.
- Implements retry mechanisms and error handling for robust API interactions.
- Generates a concise summary of the input document.

3. Knowledge Graph Generation (GraphMaker.py)

- Uses the LangChain library to split the summary into manageable chunks.
- Employs a custom ontology to define entity types and relationships.
- Utilizes the Ollama model to extract entities and relationships from the text.
- Constructs a knowledge graph based on the extracted information.
- Visualizes the graph using Graphviz, with customizable appearance settings.

4. Workflow Orchestration (run.py)

- Coordinates the execution of all components in the correct sequence.
- Manages temporary file creation and cleanup.

## Examples

### Abstract

Here's the rewritten text in the specified format:

**Title:** Fine-Tuning Large Language Models with Human-Inspired Learning Strategies for Medical Question Answering

**Abstract:**
This study evaluates fine-tuning large language models (LLMs) with human-inspired learning strategies for medical question answering, covering four key dimensions: learning strategies, models, datasets, and data labelling scenarios. The results show moderate accuracy gains from adopting human-inspired learning strategies, significant variability in the effectiveness of learning strategies across model-dataset combinations, and the potential of LLM-defined difficulty measures as a cost-effective alternative to human-defined metrics for curriculum design.

**Introduction:**
The fine-tuning of large language models (LLMs) has become a crucial technique for improving performance on various natural language processing tasks. This study focuses on applying human-inspired learning strategies to fine-tune LLMs for medical question answering, exploring their potential benefits and limitations.

**Methodology:**
We conducted an extensive evaluation of fine-tuning LLMs with human-inspired learning strategies across four key dimensions:

*   Learning Strategies:
    *   Interleaved Learning: Alternate between different categories or difficulties.
    *   Curriculum-Based Learning: Order questions by difficulty, from easy to hard.
    *   Clustered Categories: Group similar questions together and alternate between clusters.
    *   Random Sampling: Randomly sample questions without any specific strategy.
*   Models:
    *   Llama 7B: A large language model with 7 billion parameters.
    *   Mistral 7B: Another large language model with 7 billion parameters.
*   Datasets:
    *   LEK Dataset: A medical question answering dataset with limited human labels.
    *   MedQA Training Set: A larger medical question answering training set.
*   Data Labelling Scenarios:
    *   Human-Defined Difficulty: Label questions by difficulty based on human annotations.
    *   LLM-Defined Difficulty: Measure difficulty using the model's own performance and perplexity.

**Results:**

1.  **Moderate Accuracy Gains:** Adopting human-inspired learning strategies showed moderate impacts for fine-tuning performance, with maximum accuracy gains of 1.77% per model and 1.81% per dataset.
2.  **Significant Variability:** Evaluating across model-dataset combinations revealed significant variability in the effectiveness of learning strategies, with no single strategy universally outperforming the others across all models and datasets.
3.  **LLM-Defined Difficulty:** Using LLM-defined difficulty measures led to moderate accuracy improvements for curriculum-based learning strategies when compared to human-defined difficulty.

**Conclusion:**
This study demonstrates the potential benefits of fine-tuning large language models with human-inspired learning strategies for medical question answering, as well as the limitations and future directions of this approach.

**Limitations and Future Work:**

1.  **Dependent Samples:** The experiments relied on dependent samples due to the repeated nature of fine-tuning.
2.  **LLM-Defined Difficulty:** The results heavily depend on the choices of LLMs and their pre-training knowledge.
3.  **Small Dataset Size:** The LEK dataset may not fully reveal the effects of learning strategies that only emerge with more training data.
4.  **Future Research Directions:**
    *   Investigate alternative clustering algorithms for category labelling with balanced data sampling.
    *   Explore larger language models and specialized LLMs to further assess how model size and pre-training knowledge affect the impact of learning strategies.

**References:** [Shao et al., 37]

### Knowledge Graph

![kg](https://i.ibb.co/mCHFjpP/knowledge-graph.png")