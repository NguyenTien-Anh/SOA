from llama_index.core import PromptTemplate
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.post("/gen-sub-topic")
def select_topic(topic, quantity):
    QA_PROMPT_TOPIC = PromptTemplate(PROMPT_TEMPLATE_TOPIC)
    query_engine_topic = data.as_query_engine(
        similarity_top_k=3, text_qa_template=QA_PROMPT_TOPIC,
        llm=OpenAI(model='gpt-4o-mini', temperature=0.1, max_tokens=512),
        max_tokens=-1
    )
    if topic != '':
        select_topic_prompt = "Hãy chọn " + str(quantity) + " nội dung liên quan đến chủ đề \"" + topic + "\""
    else:
        select_topic_prompt = "Hãy chọn " + str(quantity) + " nội dung bất kì trong dữ liệu bạn có"

    select_topic_prompt += (f", Câu trả lời bạn đưa ra duy nhất chỉ là định dạng json có nội dung: " +
                            "{\"topics\": [nội dung 1, nội dung 2, nội dung 3, ...]}")
    response = query_engine_topic.query(select_topic_prompt)
    subTopics = json.loads(str(response))
    return subTopics["topics"]