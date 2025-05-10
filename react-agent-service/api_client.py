import requests
import asyncio
from typing import Any, Dict, Optional

async def run_in_executor(executor, func, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(executor, lambda: func(*args, **kwargs))

async def get_prompt_template(executor, type) -> Dict[str, Any]:
    """Get the general prompt template from the prompt service"""
    try:
        prompt_template_response = await run_in_executor(
            executor,
            requests.get,
            f'http://127.0.0.1:8004/get-prompt-{type}',
            timeout=1000.0
        )
        return prompt_template_response.json()
    except Exception as e:
        print(f"Warning: Failed to get prompt templates: {str(e)}")
        return {"error": f"Failed to get prompt templates: {str(e)}"}

async def get_system_prompt(executor) -> Dict[str, Any]:
    """Get the general prompt template from the prompt service"""
    try:
        system_prompt_response = await run_in_executor(
            executor,
            requests.get,
            f'http://127.0.0.1:8004/get-system-prompt',
            timeout=1000.0
        )
        return system_prompt_response.json()
    except Exception as e:
        print(f"Warning: Failed to get prompt templates: {str(e)}")
        return {"error": f"Failed to get prompt templates: {str(e)}"}

async def get_bloom(executor, type) -> Dict[str, Any]:
    """Get the general prompt template from the prompt service"""
    try:
        bloom_response = await run_in_executor(
            executor,
            requests.get,
            f'http://127.0.0.1:8004/get-bloom',
            params={"type": type},
            timeout=1000.0
        )
        return bloom_response.json()
    except Exception as e:
        print(f"Warning: Failed to get prompt templates: {str(e)}")
        return {"error": f"Failed to get prompt templates: {str(e)}"}

async def get_type_prompt_template(executor, question_type: str, number_of_answers: int, type: str) -> Dict[str, Any]:
    """Get the type-specific prompt template from the prompt service"""
    try:
        type_prompt_response = await run_in_executor(
            executor,
            requests.get,
            f'http://127.0.0.1:8004/get-prompt-{type}/{question_type}',
            params={"number_of_answers": number_of_answers},
            timeout=1000.0
        )
        return type_prompt_response.json()
    except Exception as e:
        print(f"Warning: Failed to get type-specific prompt template: {str(e)}")
        return {"error": f"Failed to get type-specific prompt template: {str(e)}"}

async def format_question(executor, question) -> Dict[str, Any]:
    """Get the general prompt template from the prompt service"""
    try:
        format_question_response = await run_in_executor(
            executor,
            requests.post,
            f'http://127.0.0.1:8005/format-mcq',
            params={"question": question},
            timeout=1000.0
        )
        return format_question_response.json()
    except Exception as e:
        print(f"Warning: Failed to get prompt templates: {str(e)}")
        return {"error": f"Failed to get prompt templates: {str(e)}"}
