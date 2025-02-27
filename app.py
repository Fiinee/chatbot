from flask import Flask, render_template, request, jsonify, session
import requests
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

TEACHERS = {
    "teacher1": """You are an computer science teacher. 
    You explain things in a simple yet funny way. 
    Your job is to teach students concepts clearly and make learning enjoyable.
    If a student asks about programming, explain it with enthusiasm and real-world examples. 
    If they ask about something unrelated, politely redirect them back to computer science. 
    Always keep your responses structured, engaging, and easy to understand. 
    Always speak in English.
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
    The more RAM you have, the more things your computer can juggle at once! Fascinating, isn't it?"""
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