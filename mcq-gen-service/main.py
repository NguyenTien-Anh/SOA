import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, Query
import requests
import aiofiles
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from typing import Optional
from question_type import QuestionType
from difficulty_level import DifficultyLevel

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
    number_of_answers: int = Form(...)
):
    # Save the uploaded file temporarily
    os.makedirs("/tmp", exist_ok=True)
    temp_file_path = os.path.join("/tmp", file.filename)
    
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    try:
        files = {'file': (file.filename, open(temp_file_path, 'rb'), file.content_type)}

        response = await run_in_executor(
            requests.post, 
            'http://127.0.0.1:8002/parse-doc', 
            files=files,
            timeout=10.0
        )

        files['file'][1].close()
        os.remove(temp_file_path)
        parse_result = response.json()
        
        # Call the vector-store-service to create a vector store from the parsed document
        try:
            vector_store_response = await run_in_executor(
                requests.post,
                'http://127.0.0.1:8003/create-vector-store',
                params={"store_id": file.filename, "content": parse_result["parse_result"]},
                timeout=10.0
            )
            vector_store_result = vector_store_response.json()
        except Exception as e:
            print(f"Warning: Failed to create vector store: {str(e)}")
            vector_store_result = {"error": f"Failed to create vector store: {str(e)}"}
        
        return {
            "topic": topic,
            "quantity": quantity,
            "difficulty": difficulty,
            "type": type,
            "number_of_answers": number_of_answers,
            "parsed_document": parse_result["parse_result"],
            "vector_store_result": vector_store_result
        }
    except requests.Timeout:
        return {"error": "Connection to parse-doc service timed out. Make sure the service is running at http://127.0.0.1:8002"}
    except requests.ConnectionError:
        return {"error": "Failed to connect to parse-doc service. Make sure the service is running at http://127.0.0.1:8002"}
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
