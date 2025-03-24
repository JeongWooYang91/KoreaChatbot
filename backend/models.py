from pydantic import BaseModel
from typing import List, Dict

class ScenarioRequest(BaseModel):
    Name: str
    Nationality: str
    NativeLanguage: str
    Living_in_Korea: str
    Duration_of_Stay: str
    Visa_Type: str
    Industry: str
    Work_Experience: str
    Korean_Test_Score: str
    Duration_of_Korean_Study: str
    Interests: str
    Hobbies: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
