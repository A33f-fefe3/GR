from langchain_community.vectorstores import FAISS
from element.qinfanapi import create_llm,create_embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader,TextLoader,CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def combine_documents(documents):
    return "\n".join(doc.page_content for doc in documents)

# 加载模型
llm = create_llm()
embedding =create_embeddings()

# 循环加载文件夹数据
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

# 加载PDF数据
loader = PyPDFLoader("data\万维钢：拐点—站在AI颠覆世界的前夜 copy.pdf", extract_images=True)
pages = loader.load_and_split()
texts = combine_documents(pages)
text_splitter = RecursiveCharacterTextSplitter(texts,chunk_size=200, chunk_overlap=20)
documents = text_splitter.split_documents(documents=pages)

# 创建向量数据库，向量化后保存
db = FAISS.from_documents(documents, embedding)
db.save_local("./faiss_index")
# 如果已经创建好了，可以直接读取
# db = FAISS.load_local("./faiss_index", embedding, allow_dangerous_deserialization=True)


# 加载csv知识图谱
# loader = CSVLoader(file_path="get_relation_data1.csv",encoding='utf-8')
# docs = loader.load()
text_loader_kwargs = {'autodetect_encoding': True}
loader = DirectoryLoader(
    "relation_data", 
    glob="**/[!.]*", 
    loader_cls=CSVLoader, 
    silent_errors=True,
    loader_kwargs=text_loader_kwargs, 
    show_progress=True,
    use_multithreading=True, 
    max_concurrency=4,
    exclude=[], 
    recursive=True
)
docs = loader.load()

# 创建向量数据库，向量化后保存
db2 = FAISS.from_documents(docs, embedding)
db2.save_local("./faiss_graph_index")
# 如果已经创建好了，可以直接读取
# db2 = FAISS.load_local("./faiss_graph_index", embedding, allow_dangerous_deserialization=True)


while True:
    query = input("\n用户:")
    # 执行相似度搜索并合并文档内容
    embedding_vector = embedding.embed_query(query)
    docs = db.similarity_search_by_vector(embedding_vector, k=6)
    combined_content_docs = combine_documents(docs)

    # 执行另一个相似度搜索并合并文档内容
    embedding_vector = embedding.embed_query(query)
    graph = db2.similarity_search_by_vector(embedding_vector, k=6)
    combined_content_graph = combine_documents(graph)

    full_retriever= combined_content_graph + combined_content_docs
    prompt = f"仅根据下列上下文回答问题:\nvector data:\n{combined_content_docs}\nGraph data:\n{combined_content_graph}" + f"\nQuestion: \n{query}\n使用自然语言，简洁明了."
    print(prompt)
    response=llm.invoke(prompt)
    print ("\n文心一言:",response)