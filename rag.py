import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


PDF_FILE = "data/nutrition.pdf"
VECTOR_DB = "vector_db"


def create_rag():

    if not os.path.exists(PDF_FILE):
        raise FileNotFoundError(
            f"Nutrition PDF not found: {PDF_FILE}"
        )

    # Load PDF
    document = PyPDFLoader(PDF_FILE).load()

    # Split PDF into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(document)

    # Create embeddings
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create FAISS database
    db = FAISS.from_documents(chunks, embedding)

    # Save database
    db.save_local(VECTOR_DB)

    return db


def load_rag():

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # If vector database already exists
    if (
        os.path.exists(os.path.join(VECTOR_DB, "index.faiss"))
        and os.path.exists(os.path.join(VECTOR_DB, "index.pkl"))
    ):

        db = FAISS.load_local(
            VECTOR_DB,
            embedding,
            allow_dangerous_deserialization=True
        )

        return db

    # If database does not exist, create it
    else:

        print("Vector database not found. Creating new RAG database...")

        return create_rag()