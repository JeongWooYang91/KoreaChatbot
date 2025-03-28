import React, { useEffect, useRef, useState } from "react";
import { useUser } from "../context/UserContext";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const ChatbotPage = () => {
  const { selectedScenario } = useUser();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

  const handleVoiceInput = () => {
    if (!recognition) {
      alert("🎤 이 브라우저는 음성 인식을 지원하지 않습니다.");
      return;
    }
  
    setIsListening(true);
  
    recognition.start();
  
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("🎙️ Transcribed:", transcript);
      setInput(transcript); // Or handleSend(transcript) if you want instant send
      setIsListening(false);
    };
  
    recognition.onerror = (event) => {
      console.error("🎤 Speech recognition error:", event.error);
      setIsListening(false);
    };
  
    recognition.onend = () => {
      setIsListening(false);
    };
  };

const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
  recognition.lang = "ko-KR";         // Korean
  recognition.continuous = false;     // One-shot recognition
  recognition.interimResults = false;
}

  // Initialize chat with system and scenario
  useEffect(() => {
    if (!selectedScenario) {
      navigate("/scenarios");
      return;
    }

    setMessages([
      {
        role: "system",
        content: "You are a Korean conversation partner helping the user practice Korean.",
      },
      {
        role: "assistant",
        content: selectedScenario.content,
      },
    ]);
  }, [selectedScenario, navigate]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const updatedMessages = [...messages, { role: "user", content: input }];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        messages: updatedMessages,
      });

      setMessages([...updatedMessages, { role: "assistant", content: res.data.reply }]);
    } catch (err) {
      console.error("Chatbot error:", err);
      setMessages([...updatedMessages, { role: "assistant", content: "⚠️ 응답을 가져오는 데 실패했습니다." }]);
    } finally {
      setLoading(false);
    }
  };

  

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">💬 챗봇과 대화하기</h2>

      <div className="border rounded p-3 mb-3" style={{ height: "400px", overflowY: "auto", background: "#f9f9f9" }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-2 ${msg.role === "user" ? "text-end" : "text-start"}`}>
            <strong>{msg.role === "user" ? "🧑 나" : "🤖 챗봇"}</strong>
            <div>{msg.content}</div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <textarea
        className="form-control mb-2"
        rows={2}
        placeholder="메시지를 입력하세요..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />

<div className="d-flex gap-2">
  <button className="btn btn-primary" onClick={handleSend} disabled={loading}>
    {loading ? "응답 중..." : "보내기"}
  </button>

  <button
    className={`btn ${isListening ? "btn-danger" : "btn-outline-secondary"}`}
    onClick={handleVoiceInput}
    disabled={loading}
  >
    {isListening ? "🎙️ 듣는 중..." : "🎤 말하기"}
  </button>
</div>
    </div>
  );
};

export default ChatbotPage;
