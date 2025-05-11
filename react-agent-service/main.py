import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex, Document
from prompt_formatter import create_prompt_formats
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from api_client import get_prompt_template, format_question, get_bloom, get_system_prompt
from concurrent.futures import ThreadPoolExecutor
from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
import json

load_dotenv()

app = FastAPI()

_executor = ThreadPoolExecutor(max_workers=10)

vector_stores = {}
tools = {}

@app.post("/create-vector-store")
def create_vector_store(request_data: dict):
    store_id = request_data.get("store_id", "default")
    content = request_data.get("content")

    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
    gpt_documents = [Document(text=content)]
    data = VectorStoreIndex.from_documents(
        documents=gpt_documents,
        transformations=[text_splitter],
        show_progress=True
    )
    vector_stores[store_id] = data
    return store_id

@app.post("/create-query-engine-tool")
async def create_query_engine(store_id, type, number_of_answers):
    qa_prompt_gen_format, qa_prompt_eval_format = await create_prompt_formats(type, number_of_answers)

    gen_query_engine = vector_stores[store_id].as_query_engine(
        similarity_top_k=3,
        text_qa_template=qa_prompt_gen_format,
        llm=OpenAI(model='gpt-4o-mini', temperature=0.5, max_tokens=512),
        max_tokens=-1
    )

    eval_query_engine = vector_stores[store_id].as_query_engine(
        similarity_top_k=3,
        text_qa_template=qa_prompt_eval_format,
        llm=OpenAI(model='gpt-4o-mini', temperature=0.1, max_tokens=512),
        max_tokens=-1
    )

    gen_tool = QueryEngineTool(
        query_engine=gen_query_engine,
        metadata=ToolMetadata(
            name="Gen",
            description=(
                "Đầu vào là một yêu cầu. Đầu ra là một câu hỏi trắc nghiệm và có chỉ rõ đáp án đúng."
                "Tạo câu hỏi trắc nghiệm về nội dung được yêu cầu."
                "Sử dụng các công cụ khác để đánh giá câu hỏi."
            ),
        )
    )

    eval_tool = QueryEngineTool(
        query_engine=eval_query_engine,
        metadata=ToolMetadata(
            name="Eval",
            description=(
                "Đầu vào là một câu hỏi trắc nghiệm. Đầu ra là 1 câu đánh giá và 1 câu hỏi trắc nghiệm. "
                "Hãy chỉ rõ câu trả lời đúng."
                "Tiến hành đánh giá câu hỏi. Giải thích câu trả lời đúng, nếu câu hỏi hoặc câu trả lời "
                "sai thì thực hiện chỉnh sửa lại."
                "Nếu không có câu trả lời đúng thì hãy sửa lại câu trả lời."
                "Nếu các đáp án tương tự nhau thì hãy sửa lại."
                "Cải thiện câu hỏi trắc nghiệm."
                "Kết quả cuối cùng là 1 câu hỏi trắc nghiệm."
            )
        )
    )

    tools["gen"] = gen_tool
    tools["eval"] = eval_tool

    return "gen", "eval"

async def gen_sub_topic(store_id, topic, quantity):
    data = vector_stores[store_id]
    prompt_template_topic = await get_prompt_template(_executor, "topic")
    qa_prompt_topic = PromptTemplate(prompt_template_topic["prompt_template"])
    query_engine_topic = data.as_query_engine(
        similarity_top_k=3, text_qa_template=qa_prompt_topic,
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

@app.post("/mcq-gen")
async def mcq_gen(store_id, topic, quantity, difficulty, number_of_answers, recheck, type):
    react_agent_tool = [tools["gen"]]
    bloom_dict = {
        "nhớ": "Câu hỏi yêu cầu người học ghi nhớ hoặc nhận diện thông tin đã học trước đó. Câu hỏi chỉ yêu cầu người học có thể nhớ lại các sự kiện, khái niệm, thuật ngữ, hoặc định nghĩa mà họ đã học. Câu hỏi ở cấp độ này chỉ yêu cầu nhớ lại thông tin, không yêu cầu giải thích hay phân tích gì thêm. Ví dụ: 'Đâu là năm diễn ra Cách mạng Tháng Tám ở Việt Nam?' \nA. 1945 \nB. 1954 \nC. 1975 \nD. 1986",
        "hiểu": "Câu hỏi yêu cầu người học giải thích hoặc diễn giải ý nghĩa của thông tin đã học. Người học phải hiểu và nắm vững ý nghĩa của thông tin trước khi có thể diễn đạt lại bằng từ ngữ của mình. Câu hỏi này yêu cầu người học phải làm rõ những gì họ đã học thay vì chỉ đơn giản là nhớ thông tin. Ví dụ: 'Chọn câu trả lời đúng nhất để giải thích tại sao lá cây có màu xanh?' \nA. Do chứa diệp lục hấp thụ ánh sáng xanh \nB. Do chứa diệp lục phản xạ ánh sáng xanh \nC. Do chứa nước trong tế bào lá \nD. Do chứa các sắc tố hấp thụ tất cả ánh sáng ngoại trừ xanh",
        "áp dụng": "Câu hỏi yêu cầu sử dụng kiến thức đã học trong các tình huống thực tế. Người học cần phải áp dụng các lý thuyết hoặc nguyên lý vào một tình huống mới. Đây là cấp độ yêu cầu người học sử dụng các công cụ hoặc quy tắc đã học để giải quyết vấn đề. Ví dụ: 'Nếu một tam giác có hai cạnh là 3 cm và 4 cm, đâu là độ dài cạnh huyền?' \nA. 5 cm \nB. 6 cm \nC. 7 cm \nD. 8 cm"
    }
    bloom = bloom_dict[difficulty]
    if recheck == "True":
        react_agent_tool.append(tools["eval"])
    react_agent = ReActAgent.from_tools(
        react_agent_tool,
        llm=OpenAI(model="gpt-4o-mini"),
        verbose=True,
    )
    react_system_header_str = await get_system_prompt(_executor)
    react_system_prompt = PromptTemplate(react_system_header_str["prompt_template"])
    react_agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    react_agent.reset()
    type_dict = {
        "MultipleChoice": f"Tạo 1 câu hỏi trắc nghiệm MultipleChoice gồm {number_of_answers} "
                          f"đáp án và có ít nhất 2 đáp án đúng. ",
        "SingleChoice": f"Tạo 1 câu hỏi trắc nghiệm SingleChoice gồm {number_of_answers} "
                        f"đáp án và có 1 đáp án đúng, {int(number_of_answers) - 1} đáp án sai.",
        "TrueFalse": f"Tạo 1 câu hỏi trắc nghiệm TrueFalse chỉ gồm 2 loại đáp án "
                     f"đúng hoặc sai và có 1 đáp án đúng, 1 đáp án sai.",
    }
    mcqs = []
    topics = await gen_sub_topic(store_id, topic, quantity)
    for i in range(0, int(quantity)):
        if i > len(topics) - 1:
            continue
        topic_item = topics[i]
        prompt = (f"{type_dict[type]} Câu hỏi có nội dung liên quan đến {topic_item}"
                  f" trong chủ đề {topic}. {bloom}")
        if recheck == "True":
            prompt = prompt + "Sau khi tạo câu hỏi sử dụng công cụ kiểm tra lại."
        question = react_agent.chat(prompt)
        result = await format_question(_executor, question)
        format_mcq = result["format_question"]
        mcqs.append(format_mcq)
    return mcqs


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)
