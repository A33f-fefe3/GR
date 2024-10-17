import time
import traceback
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from typing import List
from element.qinfanapi import create_llm,create_embeddings
from element.node import clean_graph_document,showGraph
from element.save import create_fulltext_index,export_all_relationships_to_csv,export_all_relationships_to_csv_relation
from element.clear import clear_neo4j_database
from langchain_community.document_loaders import DirectoryLoader,TextLoader,PyPDFLoader,PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def combine_documents(documents):
    return "\n".join(doc.page_content for doc in documents)

# 删除数据库文件
clear_neo4j_database("bolt://localhost:7687", "neo4j", "12345678")


graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="12345678")
print("数据库连接")


# 加载数据
# text_loader_kwargs = {'autodetect_encoding': True}
# loader = DirectoryLoader(
#     "data", 
#     glob="**/[!.]*", 
#     loader_cls=TextLoader, 
#     silent_errors=True,
#     loader_kwargs=text_loader_kwargs, 
#     show_progress=True,
#     use_multithreading=True, 
#     max_concurrency=4,
#     exclude=[], 
#     recursive=True
# )
# docs = loader.load()
# texts = combine_documents(docs)
# text_splitter = RecursiveCharacterTextSplitter(texts,chunk_size=500, chunk_overlap=20)
# documents = text_splitter.split_documents(documents=docs)



loader = PyMuPDFLoader("data/Inner Mastery, Outer Impact_Hitendra Wadhwa_liber3.pdf")
pages = loader.load_and_split()
texts = combine_documents(pages)
text_splitter = RecursiveCharacterTextSplitter(texts,chunk_size=200, chunk_overlap=20)
documents = text_splitter.split_documents(documents=pages)
# print(documents[7])
print(len(documents))
# documents = documents[100:5000]

# 问模型
llm = create_llm()
# 创建LLM到图文档的转换器
llm_transformer = LLMGraphTransformer(llm=llm)

# 设置每次处理的文档数量
batch_size = 1
# 设置最大重试次数
max_retries = 3
# 设置重试之间的延迟时间（秒）
retry_delay = 1

for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 尝试将当前批次转换为图文档
            graph_documents = llm_transformer.convert_to_graph_documents(batch)
            # print(graph_documents)
            # 清理奇怪的符号（如果需要的话）
            # cleaned_graph_documents = [clean_graph_document(doc) for doc in graph_documents]  # type: ignore
            
            # 索引节点
            graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
            
            # 构建知识图谱
            showGraph()
            print(f'Batch {i // batch_size} processed successfully.')
            break  # 如果没有错误，跳出循环，处理下一个批次
        except Exception as e:
            # 如果发生错误，打印错误信息，并增加重试计数
            print(f"Error processing batch {i // batch_size}, attempt {retry_count + 1}/{max_retries}: {e}")
            traceback.print_exc()
            retry_count += 1
            if retry_count < max_retries:
                # 在下一次尝试之前等待一段时间
                time.sleep(retry_delay)
            else:
                print(f"Failed to process batch {i // batch_size} after {max_retries} attempts. Moving on to the next batch.")

# 调用函数导出所有关系数据
# export_all_relationships_to_csv()
# 导出图标关系
export_all_relationships_to_csv_relation()
