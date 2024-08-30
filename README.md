# PDF-Summary-Knowledge-Graph-Generator

## 使用步骤

1. 启动Ollama`ollama serve`
2. 安装依赖

```bash
pip install PyMuPDF beautifulsoup4 tqdm python-dotenv requests langchain langchain-community graphviz knowledge-graph-maker
```

2. 配置`.env`文件
3. 运行`PDFParser.py`将pdf转换为txt
4. 运行`Ollama.py`生成摘要文件`ouutput.txt`
5. 运行`GraphMaker.py`生成知识图谱`knowledge_graph.png`

## 样例

摘要：
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
知识图谱：
![知识图谱](https://i.ibb.co/mCHFjpP/knowledge-graph.png")