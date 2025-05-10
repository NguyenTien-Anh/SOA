import requests
import asyncio
from typing import Any, Dict, Optional

async def run_in_executor(executor, func, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(executor, lambda: func(*args, **kwargs))

async def parse_doc(executor, files: Dict) -> Dict[str, Any]:
    """Parse a document using the document parsing service"""
    try:
        response = await run_in_executor(
            executor,
            requests.post,
            'http://127.0.0.1:8002/parse-doc',
            files=files,
            timeout=1000.0
        )
        return response.json()
    except requests.Timeout:
        return {"error": "Connection to parse-doc service timed out. Make sure the service is running at http://127.0.0.1:8002"}
    except requests.ConnectionError:
        return {"error": "Failed to connect to parse-doc service. Make sure the service is running at http://127.0.0.1:8002"}
    except Exception as e:
        return {"error": f"An error occurred while parsing document: {str(e)}"}

async def create_vector_store(executor, store_id: str, content: str) -> Dict[str, Any]:
    """Create a vector store from parsed document content"""
    try:
        vector_store_response = await run_in_executor(
            executor,
            requests.post,
            'http://127.0.0.1:8003/create-vector-store',
            params={"store_id": store_id, "content": content},
            timeout=1000.0
        )
        return vector_store_response.json()
    except Exception as e:
        print(f"Warning: Failed to create vector store: {str(e)}")
        return {"error": f"Failed to create vector store: {str(e)}"}

async def create_query_engine_tool(executor, store_id: str, type: str, number_of_answers: int) -> Dict[str, Any]:
    """Create a query engine tool using the react-agent-service"""
    try:
        response = await run_in_executor(
            executor,
            requests.post,
            'http://127.0.0.1:8003/create-query-engine-tool',
            params={"store_id": store_id, "type": type, "number_of_answers": number_of_answers},
            timeout=1000.0
        )
        return response.json()
    except requests.Timeout:
        return {"error": "Connection to react-agent-service timed out. Make sure the service is running at http://127.0.0.1:8003"}
    except requests.ConnectionError:
        return {"error": "Failed to connect to react-agent-service. Make sure the service is running at http://127.0.0.1:8003"}
    except Exception as e:
        return {"error": f"An error occurred while creating query engine tool: {str(e)}"}

async def create_mcq(executor, store_id: str, topic: str, quantity: int, difficulty: str,
                     number_of_answers: int, recheck: bool, type: str) -> Dict[str, Any]:
    """Create a vector store from parsed document content"""
    try:
        mcq_response = await run_in_executor(
            executor,
            requests.post,
            'http://127.0.0.1:8003/mcq-gen',
            params={
                "store_id": store_id,
                "topic": topic,
                "quantity": quantity,
                "difficulty": difficulty,
                "number_of_answers": number_of_answers,
                "recheck": recheck,
                "type": type
            },
            timeout=1000.0
        )
        return mcq_response.json()
    except Exception as e:
        print(f"Warning: Failed to create vector store: {str(e)}")
        return {"error": f"Failed to create vector store: {str(e)}"}