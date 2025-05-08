import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from llama_cloud_services import LlamaParse
import os

load_dotenv()

app = FastAPI()


@app.post("/parse-doc")
def parse_doc(file: UploadFile = File(...)):
    os.makedirs("docs", exist_ok=True)
    file_path = os.path.join("docs", file.filename)
    with open(file_path, "wb") as buffer:
        contents = file.file.read()
        buffer.write(contents)
    parser = LlamaParse(
        result_type="markdown",
        verbose=True
    )
    file_content = "\n\n".join([
        content.text for content in parser.load_data(file_path=file_path)
    ])
    return {"parse_result": file_content}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
