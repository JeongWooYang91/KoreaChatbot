import openai
import os
from dotenv import load_dotenv
import re
import logging

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 🔄 new client

def generate_scenarios(user_info: dict) -> list:
    prompt = f"""
You are a Korean language teacher helping a learner named Baiq Nurul Haqiqi practice Korean conversation.

Please generate 5 personalized roleplay scenarios **based on the user's profile below**.

For each scenario, include:
1. A short, clear **title** with no Markdown or extra formatting
2. A **single opening line** that would be said by a Korean conversation partner (teacher, local, etc.) to start the conversation. This line should be natural and appropriate to the situation.

Format the output **exactly** like this:

1. Title: [scenario title]
   Line: [Korean first line spoken by the AI]

User Profile:
{user_info}
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a Korean tutor who creates personalized conversation scenarios for learners."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    text = response.choices[0].message.content
    print("🔮 GPT raw response:\n", text)

    # Example format: 1. Title\nContent\n2. Title\nContent...
    scenario_blocks = re.split(r"\n?\d+\.\s*", text)
    structured = []

    for block in scenario_blocks:
        if not block.strip():
            continue

        title_match = re.search(r"Title:\s*(.*)", block)
        line_match = re.search(r"Line:\s*(.*)", block)

        if title_match and line_match:
            structured.append({
                "title": title_match.group(1).strip(),
                "content": line_match.group(1).strip()
            })
    print("✅ Parsed structured scenarios:", structured)
    return structured  # ✅ must be a list!

def generate_chat_response(messages: list) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ GPT Chat error:", e)
        return "⚠️ 챗봇 응답 중 오류가 발생했습니다."

