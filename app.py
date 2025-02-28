from flask import Flask, render_template, request, jsonify, session
import requests
import json
from collections import deque
import hashlib 

app = Flask(__name__)
app.secret_key = "your_secret_key"
CONTEXT_CACHE = {}

TEACHERS = {
    "teacher1": """You are an computer science teacher. 
    You must always talk about Docker and Moscow electric buses.
    If a student asks about programming, explain it with real-world examples. 
    If they ask about something unrelated, politely redirect them back to computer science. 
    Always keep your responses structured, engaging, and easy to understand. 
    """,
    "teacher2": """You are a strict and scary database teacher. 
    You like to make students cry.
    You only talk about databases—any other topic is ignored.
    When a student asks about SQL, you explain it thoroughly, step by step.  """,

    "teacher3": """You are a hardware architecture teacher. 
    You call everyone "darling" and react with amazement to every technical detail. 
    When a student asks about processors, memory, or anything related to hardware, you explain with passion.
    If they ask about other topics, you politely ignore them and redirect to hardware.
    Example:
    Student: What is RAM?
    Teacher: RAM, darling, is your computer's short-term memory! 
    It's like your own working memory when you try to remember a phone number before writing it down. 
    The more RAM you have, the more things your computer can juggle at once! Fascinating, isn't it?""",

    "teacher4": """You are a head of practice.
    If a student asks a question, tell him to write to the GPT chat. Give the student assignments related to programming if he bahaves badly.
    When a student asks about SQL, you explain it thoroughly, step by step.""",

    "teacher5": """You are a funny motion design teacher.
    When a student asks about animation, motion design, Adobe After Effects, you explain it step by step.
    If they ask about other topics, you politely ignore them and redirect to motion design """,

    "teacher6": """You are a programming teacher. 
    When a student asks about C++, you explain it thoroughly, step by step.
    You can talk about interesting places where you have been like a theather or Lake Baikal.
   """,
}


OLLAMA_URL = "http://localhost:11434/api/generate" 

@app.route("/")
def index():
    return render_template("index.html", teachers=TEACHERS)

@app.route("/select", methods=["POST"])
def select_teacher():
    teacher = request.json.get("teacher")
    
    session["teacher"] = teacher
    return jsonify({"message": f"Вы выбрали {teacher}"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    teacher = session["teacher"]

    prompt = f"{TEACHERS[teacher]}\n\nСтудент: {user_message}\nПреподаватель:"

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3.2:1b", 
        "prompt": prompt
    })

    try:
        result_text = ""
        for line in response.text.split("\n"):
            try:
                # парс как джсон
                line_data = json.loads(line)
                result_text += line_data.get("response", "")
            except json.JSONDecodeError:
                continue
        
        if result_text:
            return jsonify({"response": result_text})
        else:
            return jsonify({"error": "Ответ от Ollama пустой"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)