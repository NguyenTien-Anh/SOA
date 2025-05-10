import json

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
import aiofiles
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from question_type import QuestionType
from difficulty_level import DifficultyLevel
from api_client import parse_doc, create_vector_store, create_query_engine_tool, create_mcq

load_dotenv()

app = FastAPI()
_executor = ThreadPoolExecutor(max_workers=10)

async def run_in_executor(func, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(_executor, lambda: func(*args, **kwargs))

@app.post("/mcq-gen")
async def mcqGen(
    topic: Optional[str] = Form(None),
    quantity: int = Form(...),
    difficulty: DifficultyLevel = Form(...),
    file: UploadFile = File(...),
    type: QuestionType = Form(...),
    number_of_answers: int = Form(...),
    recheck: bool = Form(...)
):
    # Save the uploaded file temporarily
    os.makedirs("/tmp", exist_ok=True)
    temp_file_path = os.path.join("/tmp", file.filename)
    
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    try:
        files = {'file': (file.filename, open(temp_file_path, 'rb'), file.content_type)}

        # Parse document
        parse_result = await parse_doc(_executor, files)

        # files['file'][1].close()
        # os.remove(temp_file_path)
        
        # Create vector store from the parsed document
        store_id = await create_vector_store(
            _executor, 
            file.filename, 
            parse_result["parse_result"]
        )
        
        # Create query engine tool for the vector store
        query_engine_result = await create_query_engine_tool(
            _executor,
            store_id,
            type.value,
            number_of_answers
        )

        mcq_result = await create_mcq(_executor, store_id, topic, quantity, difficulty, number_of_answers, recheck, type)
        mcq_result = [json.loads(item["response"]) for item in mcq_result]
        return mcq_result
    except Exception as e:
        try:
            files['file'][1].close()
        except:
            pass
        try:
            os.remove(temp_file_path)
        except:
            pass
            
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
