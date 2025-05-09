import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex, Document

load_dotenv()

app = FastAPI()

vector_stores = {}

@app.post("/create-vector-store")
def create_vector_store(content, store_id: str = "default"):
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    gpt_documents = [Document(text=content)]
    data = VectorStoreIndex.from_documents(
        documents=gpt_documents,
        transformations=[text_splitter],
        show_progress=True
    )
    vector_stores[store_id] = data
    return {"message": f"Vector store created and stored with ID: {store_id}"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)
