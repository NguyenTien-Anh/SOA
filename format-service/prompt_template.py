SYSTEM_PROMPT = (
    "Hãy định dạng lại câu hỏi thành duy nhất một json có nội dung {\"question\": câu hỏi trắc nghiệm"
    "\"answers\": [{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, "
    "{\"answer\": đáp án 1, \"isCorrectAnswer\": \"true\" nếu đáp án đúng và \"false\" nếu ngược lại}, ...]} "
    "mà không thêm bất kì dòng chữ nào khác. Ví dụ câu hỏi bạn nhận được là:\n"
    "Câu hỏi trắc nghiệm: Mô hình kiến trúc 3 mức cơ sở dữ liệu trong chủ đề Mô hình cơ sở dữ liệu bao gồm "
    "những mức nào?\nA) Mức trong\nB) Mức mô hình dữ liệu\nC) Mức ngoài\nD) Mức trung tâm\nĐáp án đúng: A) "
    "Mức trong, B) Mức mô hình dữ liệu'\n"
    "Câu trả lời chính xác bạn cần đưa ra là: "
    "{'question': 'Mô hình kiến trúc 3 mức cơ sở dữ liệu trong chủ đề Mô hình cơ sở dữ "
    "liệu bao gồm những mức nào?', 'answers': [{'answer': 'A) Mức trong', 'isCorrectAnswer': 'true'}, "
    "{'answer': 'B) Mức mô hình dữ liệu', 'isCorrectAnswer': 'true'}, {'answer': 'C) Mức ngoài', "
    "'isCorrectAnswer': 'false'}, {'answer': 'D) Mức trung tâm', 'isCorrectAnswer': 'false'}]}"
)