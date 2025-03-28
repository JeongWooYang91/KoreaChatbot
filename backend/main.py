from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ScenarioRequest
from gpt_utils import generate_scenarios, generate_chat_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/scenarios")
async def get_scenarios(request: Request):
    body = await request.json()
    print("🔍 Incoming JSON Payload:", body)

    scenarios = generate_scenarios(body)  # ✅ this is a list of dicts

    # Just return it directly — FastAPI will serialize to JSON
    return {"scenarios": scenarios}

@app.post("/chat")
async def chat(payload: ChatRequest):
    return {"reply": generate_chat_response(payload.messages)}