from pathlib import Path
from typing import List

from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

FAISS_INDEX_DIR = Path("faiss_db")

def ingest_rag_document(file_path: str) -> None:
    """
    - Split a PDF into chunks, embed them with Gemini, and store the
    vectors in a local FAISS index.
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_000,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(docs)

    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(FAISS_INDEX_DIR))


def get_retriever() -> FAISS:
    """
    Load the FAISS index from disk and return a retriever that
    returns the top‑k most similar chunks.
    """
    if not FAISS_INDEX_DIR.exists():
        raise RuntimeError(
            f"FAISS index not found at '{FAISS_INDEX_DIR}'. "
            "Upload a PDF first (the ingestion step will create it)."
        )

    vector_store = FAISS.load_local(
        folder_path=str(FAISS_INDEX_DIR),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )


@tool
def rag_tool(query: str) -> str:
    """
    - Retrieve the most relevant passages from the previously‑ingested PDF.

    Args:
        query: The natural‑language question or keyword string.

    Returns:
        A formatted string containing up to 5 relevant chunks. If nothing
        matches, a friendly “no results” message is returned.
    """
    retriever = get_retriever()

    try:
        documents = retriever.invoke(query)          
    except AttributeError:
        documents = retriever.get_relevant_documents(query)

    if not documents:
        return "No relevant information found."

    formatted: List[str] = []
    for idx, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown source")
        page = doc.metadata.get("page", "unknown page")
        formatted.append(
            f"Document {idx}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{doc.page_content.strip()}"
        )

    return "\n\n".join(formatted)