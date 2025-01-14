import requests

def fetch_questions(amount, difficulty, qtype):
    url = f"https://opentdb.com/api.php?amount={amount}"
    if difficulty != "Any Difficulty":
        url += f"&difficulty={difficulty.lower()}"
    if qtype != "Any Type":
        url += f"&type={'multiple' if qtype == 'Multiple Choice' else 'boolean'}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return []