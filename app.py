# app.py
import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)


def call_openai(system_prompt, user_prompt, max_tokens=800):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    resp = requests.post(OPENAI_CHAT_URL, headers=headers, json=body, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]


# @app.route("/")
# def index():
#     return render_template("index.html")

# update 1.0.1
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/blog-post-1")
def blogpost1():
    return render_template("blog-post-1.html")

@app.route("/blog-post-2")
def blogpost2():
    return render_template("blog-post-2.html")

@app.route("/blog-post-3")
def blogpost3():
    return render_template("blog-post-3.html")

@app.route("/blog-post-4")
def blogpost4():
    return render_template("blog-post-4.html")




@app.route("/api/recommend", methods=["POST"])
def recommend():
    payload = request.json or {}
    interests = payload.get("interests", [])
    skills = payload.get("skills", [])
    experience = payload.get("experience", "")
    education = payload.get("education", "")

    system_prompt = (
        "You are a career guidance assistant. Always reply with JSON only, "
        "following the exact schema provided. No explanations outside JSON."
    )

    user_prompt = json.dumps({
        "task": "career_recommendations",
        "input": {
            "interests": interests,
            "skills": skills,
            "experience": experience,
            "education": education
        },
        "schema": {
            "careers": [
                {
                    "title": "string",
                    "description": "string",
                    "salary_usd": "string or number",
                    "demand": "low|medium|high|very high",
                    "match_score": "0-100"
                }
            ],
            "skill_gap": {
                "skill_name": {"your_level": "0-100", "required_level": "0-100"}
            },
            "roadmaps": {
                "career_title": [
                    {"step": 1, "title": "string", "description": "string", "resources": ["url or text"]}
                ]
            },
            "meta": {"generated_by": "string"}
        }
    })

    try:
        raw = call_openai(system_prompt, user_prompt, max_tokens=900)
        result = json.loads(raw)
    except Exception as e:
        return jsonify({"error": str(e), "raw": raw if "raw" in locals() else None}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
