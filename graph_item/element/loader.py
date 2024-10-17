from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split_text(file_path, chunk_size, chunk_overlap):
    loader = TextLoader(file_path=file_path, encoding='utf-8')
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = text_splitter.split_documents(docs)
    return documents
def load_and_split_folder(folder_path, chunk_size, chunk_overlap):
    path = Path(folder_path)
    all_documents = []
    for file_path in path.glob('**/*'):
            if "万万没想到：用理工科思维理解世界.txt" not in str(file_path):
                continue
            print(file_path)
            documents = load_and_split_text(file_path, chunk_size, chunk_overlap)
            all_documents.extend(documents)
    return all_documents