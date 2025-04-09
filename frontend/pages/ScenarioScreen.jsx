import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useUser } from "../context/UserContext";

const ScenarioScreen = () => {
  const { userInfo, setScenarios, scenarios, setSelectedScenario } = useUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!userInfo || scenarios.length > 0) return;

    const fetchScenarios = async () => {
      try {
        setLoading(true);
        const res = await axios.post("http://15.164.219.154/scenarios", userInfo, {
          headers: { "Content-Type": "application/json" }
        });
    
        console.log("🎯 GPT Structured Response:", res.data.scenarios);
    
        // No parsing needed — the backend already returns structured JSON
        setScenarios(res.data.scenarios); 
      } catch (err) {
        console.error("Failed to fetch scenarios:", err);
        setError("시나리오를 불러오는 데 실패했습니다.");
      } finally {
        setLoading(false);
      }

      console.log("🧪 SCENARIOS:", res.data.scenarios);

      if (typeof res.data.scenarios === "string") {
        throw new Error("🚨 Backend is returning a string, not a structured list!");
      }

    };

    fetchScenarios();
  }, [userInfo, scenarios, setScenarios]);

  const handleSelect = (e) => {
    const index = parseInt(e.target.value, 10);
    setSelectedIndex(index);
  };

  const handleContinue = () => {
    if (selectedIndex !== null) {
      setSelectedScenario(scenarios[selectedIndex]);
      navigate("/chat");
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">🧠 GPT가 제안한 맞춤형 대화 시나리오</h2>

      {loading && <p>시나리오 생성 중... ⏳</p>}
      {error && <p className="text-danger">{error}</p>}

      {Array.isArray(scenarios) && scenarios.length > 0 && (
  <div className="mb-3">
    <select className="form-select" onChange={handleSelect} defaultValue="">
      <option value="" disabled>시나리오를 선택하세요</option>
      {scenarios.map((scenario, idx) => (
        <option key={idx} value={idx}>
          {scenario.title}
        </option>
      ))}
    </select>

    <button className="btn btn-primary mt-3" onClick={handleContinue} disabled={selectedIndex === null}>
      선택하고 챗봇 시작하기
    </button>
  </div>
)}
    </div>
  );
};

export default ScenarioScreen;