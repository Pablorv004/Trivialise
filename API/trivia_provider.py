def transform_questions(data):
    questions = []
    for item in data:
        question = {
            "type": item["type"],
            "difficulty": item["difficulty"],
            "category": item["category"],
            "question": item["question"],
            "correct_answer": item["correct_answer"],
            "incorrect_answers": item["incorrect_answers"]
        }
        questions.append(question)
    return questions
