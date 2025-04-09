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
  const [isListening, setIsListening] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [lastReply, setLastReply] = useState("");
  const [repeatCount, setRepeatCount] = useState(1);
  const [speakingMessageIndex, setSpeakingMessageIndex] = useState(null);

  const chatEndRef = useRef(null);

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  if (recognition) {
    recognition.lang = "ko-KR";
    recognition.continuous = false;
    recognition.interimResults = false;
  }

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
      setInput(transcript);
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

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const speak = (text, repeat = 1, index = null, lang = "ko-KR") => {
    const synth = window.speechSynthesis;
    if (!synth) return;

    synth.cancel(); // Stop any previous speech

    const speakOnce = () => {
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = lang;
      utter.pitch = 1;
      utter.rate = 1;

      utter.onstart = () => {
        setSpeakingMessageIndex(index);
      };
      utter.onend = () => {
        setSpeakingMessageIndex(null);
      };

      synth.speak(utter);
    };

    let count = 0;
    const interval = setInterval(() => {
      if (count >= repeat) {
        clearInterval(interval);
        return;
      }
      speakOnce();
      count++;
    }, 3000);
  };

  useEffect(() => {
    if (!selectedScenario) {
      navigate("/scenarios");
      return;
    }

    const system = {
      role: "system",
      content: "You are a Korean conversation partner helping the user practice Korean.",
    };
    const start = {
      role: "assistant",
      content: selectedScenario.content,
    };

    setMessages([system, start]);
    setLastReply(start.content);
    if (ttsEnabled) speak(start.content, repeatCount, 1);
  }, [selectedScenario, navigate]);

  const userMessageCount = messages.filter((m) => m.role === "user").length;
  const limitReached = userMessageCount >= 5;

  const handleSend = async () => {
    if (!input.trim() || limitReached) return;

    const updatedMessages = [...messages, { role: "user", content: input }];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://15.164.219.154/chat", {
        messages: updatedMessages,
      });

      const reply = res.data.reply;
      const newMessages = [...updatedMessages, { role: "assistant", content: reply }];
      setMessages(newMessages);
      setLastReply(reply);

      if (ttsEnabled) speak(reply, repeatCount, newMessages.length - 1);
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
          <div
            key={idx}
            className={`mb-2 ${msg.role === "user" ? "text-end" : "text-start"}`}
            style={speakingMessageIndex === idx ? { background: "#fff3cd", borderRadius: "6px", padding: "4px 8px" } : {}}
          >
            <strong>{msg.role === "user" ? "🧑 나" : "🤖 챗봇"}</strong>
            <div>{msg.content}</div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <textarea
        className="form-control mb-2"
        rows={2}
        placeholder={limitReached ? "대화가 종료되었습니다." : "메시지를 입력하세요..."}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={limitReached}
      />

      <div className="d-flex flex-wrap gap-2 align-items-center">
        <button className="btn btn-primary" onClick={handleSend} disabled={loading || limitReached}>
          {loading ? "응답 중..." : "보내기"}
        </button>

        <button
          className={`btn ${isListening ? "btn-danger" : "btn-outline-secondary"}`}
          onClick={handleVoiceInput}
          disabled={loading || limitReached}
        >
          {isListening ? "🎙️ 듣는 중..." : "🎤 말하기"}
        </button>

        <button
          className={`btn ${ttsEnabled ? "btn-outline-secondary" : "btn-warning"}`}
          onClick={() => setTtsEnabled(!ttsEnabled)}
        >
          {ttsEnabled ? "🔈 음성 끄기" : "🔇 음성 켜기"}
        </button>

        <button
          className="btn btn-outline-info"
          onClick={() => speak(lastReply, repeatCount, messages.length - 1)}
          disabled={!lastReply}
        >
          🔁 다시 듣기
        </button>

        <div>
          <label className="form-label me-2">🔁 반복 횟수</label>
          <select
            className="form-select d-inline w-auto"
            value={repeatCount}
            onChange={(e) => setRepeatCount(parseInt(e.target.value))}
          >
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>{n}회</option>
            ))}
          </select>
        </div>
      </div>

      {limitReached && (
        <div className="alert alert-warning mt-4">
          🛑 <strong>이 시나리오에 대한 대화가 종료되었습니다.</strong> <br />
          새로운 시나리오를 선택해 주세요.
          <br />
          <button className="btn btn-secondary mt-2" onClick={() => navigate("/scenarios")}>
            🔄 시나리오 선택으로 이동
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatbotPage;
