import uvicorn
from fastapi import FastAPI, HTTPException
from prompt_template import SYSTEM_PROMPT, PROMPT_TEMPLATE_GEN, PROMPT_TEMPLATE_EVA, PROMPT_TEMPLATE_TOPIC
import json
import os

app = FastAPI()

# Load prompt.json data
with open(os.path.join(os.path.dirname(__file__), "prompt_gen.json"), "r", encoding="utf-8") as f:
    prompt_gen_data = json.load(f)

with open(os.path.join(os.path.dirname(__file__), "prompt_eval.json"), "r", encoding="utf-8") as f:
    prompt_eval_data = json.load(f)

with open(os.path.join(os.path.dirname(__file__), "bloom.json"), "r", encoding="utf-8") as f:
    bloom_data = json.load(f)

@app.get("/get-system-prompt")
async def get_system_prompt():
    return {"prompt_template": SYSTEM_PROMPT}

@app.get("/get-prompt-topic")
async def get_prompt_topic():
    return {"prompt_template": PROMPT_TEMPLATE_TOPIC}

@app.get("/get-prompt-gen")
async def get_prompt_gen():
    return {"prompt_template": PROMPT_TEMPLATE_GEN}

@app.get("/get-prompt-eval")
async def get_prompt_eval():
    return {"prompt_template": PROMPT_TEMPLATE_EVA}

@app.get("/get-bloom")
async def get_prompt_bloom(type: str):
    bloom = [p for p in bloom_data if p["type"] == type]
    return {"bloom": bloom}

@app.get("/get-prompt-gen/{type}")
async def get_prompt_gen_by_type(type: str, number_of_answers: int = None):
    matching_prompts = [p for p in prompt_gen_data if p["type"] == type]
    
    if not matching_prompts:
        raise HTTPException(status_code=404, detail=f"No prompts found for type: {type}")
    
    if number_of_answers is not None:
        matching_prompts = [p for p in matching_prompts if p["number_of_answers"] == number_of_answers]
        
        if not matching_prompts:
            raise HTTPException(status_code=404, detail=f"No prompts found for type: {type} with {number_of_answers} answers")
    
    # Return the first matching prompt
    selected_prompt = matching_prompts[0]
    
    return {
        "prompt_step_by_step": selected_prompt["prompt_step_by_step"],
        "prompt_example": selected_prompt["prompt_example"],
        "attention": selected_prompt["attention"]
    }


@app.get("/get-prompt-eval/{type}")
async def get_prompt_eval_by_type(type: str, number_of_answers: int = None):
    matching_prompts = [p for p in prompt_eval_data if p["type"] == type]

    if not matching_prompts:
        raise HTTPException(status_code=404, detail=f"No prompts found for type: {type}")

    if number_of_answers is not None:
        matching_prompts = [p for p in matching_prompts if p["number_of_answers"] == number_of_answers]

        if not matching_prompts:
            raise HTTPException(status_code=404,
                                detail=f"No prompts found for type: {type} with {number_of_answers} answers")

    # Return the first matching prompt
    selected_prompt = matching_prompts[0]

    return {
        "prompt_step_by_step": selected_prompt["prompt_step_by_step"],
        "prompt_example": selected_prompt["prompt_example"],
        "attention": selected_prompt["attention"]
    }

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8004, reload=True)
