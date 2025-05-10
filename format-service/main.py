import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from prompt_template import SYSTEM_PROMPT
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI

load_dotenv()

app = FastAPI()

@app.post("/format-mcq")
def format_mcq(question):
    format_agent = OpenAIAgent.from_tools(
        llm=OpenAI(model="gpt-4o-mini"),
        verbose=True,
        system_prompt=SYSTEM_PROMPT
    )

    format_question = format_agent.chat(
        f"Bạn nhận được câu hỏi trắc nghiệm sau:\n{question} "
        "Hãy định dạng lại câu hỏi thành duy nhất một json có nội dung {\"question\": câu hỏi trắc nghiệm"
        "\"answers\": [{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, "
        "{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, ...]} "
        "mà không thêm bất kì dòng chữ nào khác."
    )
    return {"format_question": format_question}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)