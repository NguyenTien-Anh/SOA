from llama_index.core import PromptTemplate
from api_client import get_prompt_template, get_type_prompt_template
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=10)

async def create_prompt_formats(type, number_of_answers):
    """
    Create formatted prompt templates for question generation and evaluation
        
    Returns:
        tuple: (qa_prompt_gen_format, qa_prompt_eval_format)
    """
    # Get prompt templates
    prompt_template_gen = await get_prompt_template(_executor, "gen")
    prompt_template_topic = await get_prompt_template(_executor, "topic")
    prompt_template_eval = await get_prompt_template(_executor, "eval")
    type_prompt_gen_template = await get_type_prompt_template(_executor, type, number_of_answers, "gen")
    type_prompt_eval_template = await get_type_prompt_template(_executor, type, number_of_answers, "eval")

    # Create generation prompt
    qa_prompt_gen = PromptTemplate(prompt_template_gen["prompt_template"])
    qa_prompt_gen_format = qa_prompt_gen.partial_format(
        prompt_step_by_step=type_prompt_gen_template["prompt_step_by_step"],
        prompt_example=type_prompt_gen_template["prompt_step_by_step"],
        attention=type_prompt_gen_template["attention"]
    )
    
    # Create evaluation prompt
    qa_prompt_eval = PromptTemplate(prompt_template_eval["prompt_template"])
    qa_prompt_eval_format = qa_prompt_eval.partial_format(
        prompt_step_by_step=type_prompt_eval_template["prompt_step_by_step"],
        prompt_example=type_prompt_eval_template["prompt_step_by_step"],
        attention=type_prompt_eval_template["attention"]
    )
    
    return qa_prompt_gen_format, qa_prompt_eval_format 