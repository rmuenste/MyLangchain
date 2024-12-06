import os
import json
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import openai
import shutil

CHROMA_PATH = "./chroma_storage"
DATA_PATH = "sim"

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        print(f"Using existing db at: {CHROMA_PATH}.")    
        return

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")    

def save_vectorstore(documents: list[Document]):
    # This will use OpenAI Embeddings to transform text into vector embeddings.
    embedding_function = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents = documents,
        embedding=embedding_function,
        persist_directory=CHROMA_PATH
    )

    print(f"Saved {len(documents)} documents to {CHROMA_PATH}.")    

def generate_data_store():
    #documents = load_documents()
    documents = []
    for document in documents:
        print(f" Doc metadata: \n {document.metadata}")

    chunks = split_text(documents)
    save_to_chroma(chunks)

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
        length_function=len,
        is_separator_regex=False
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


def load_documents():
    documents = []
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            rows = json.load(f)
    except Exception as e:
      print(f"Error loading documents: {e}")
      documents = []
      return documents

    text_content = "\n".join([f"{key}: {value}" for key, value in rows[0].items() if value])
    doc = Document(page_content=text_content, metadata={"source": ".xlsx"})
    documents.append(doc)
#    for row in rows:
#        # Convert each row to a text representation.
#        # Adjust this logic depending on your data structure.
#        text_content = "\n".join([f"{key}: {value}" for key, value in row.items() if value])
#
#        doc = Document(page_content=text_content, metadata={"source": ".xlsx"})
#        documents.append(doc)

    return documents

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

allDocs = load_documents()
print(allDocs)
save_vectorstore(allDocs)

# --------------------------------------------
# Step 4: Set up the LLM (GPT via OpenAI API)
# --------------------------------------------
# Use the OpenAI LLM. By default, this uses gpt-3.5-turbo.
# You can specify model_name="gpt-4" if you have access.
#llm = OpenAI(
#    openai_api_key=os.environ.get("OPENAI_API_KEY", "your_openai_api_key"),
#    temperature=0.0  # set to 0 for more deterministic responses
#)
#
# --------------------------------------------
# Step 5: Create a RetrievalQA Chain
# --------------------------------------------
#retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
#
#qa_chain = RetrievalQA.from_chain_type(
#    llm=llm,
#    chain_type="stuff",
#    retriever=retriever
#)
#
# --------------------------------------------
# Step 6: Query Your RAG Pipeline
# --------------------------------------------
#query = "What can we infer about the customer's preferences?"
#response = qa_chain.run(query)
#print(response)