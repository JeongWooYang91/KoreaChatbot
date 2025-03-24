import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_scenarios(user_info: dict) -> list:
    prompt = f"""
    Based on the following user profile, generate 5 personalized Korean language conversation scenarios. 
    These should be practical, short, and suitable for roleplay practice.

    User Info:
    {user_info}

    Format the response as a numbered list:
    1. ...
    2. ...
    """
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    text = res.choices[0].message.content
    scenarios = text.split("\n")
    return [s.strip() for s in scenarios if s.strip()]

def generate_chat_response(messages: list) -> str:
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    return res.choices[0].message.content.strip()