import html

def transform_questions(data):
    questions = []
    for item in data:
        question = {
            "type": item["type"],
            "difficulty": item["difficulty"],
            "category": item["category"],
            "question": html.unescape(item["question"]),
            "correct_answer": html.unescape(item["correct_answer"]),
            "incorrect_answers": [html.unescape(ans) for ans in item["incorrect_answers"]]
        }
        questions.append(question)
    print(f"Transformed {len(questions)} questions")
    return questions
