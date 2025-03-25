import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useUser } from "../context/UserContext";

const ScenarioScreen = () => {
  const { userInfo, scenarios, setScenarios, setSelectedScenario } = useUser();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!userInfo || scenarios.length > 0) return;

    const fetchScenarios = async () => {
      try {
        setLoading(true);
        const res = await axios.post("http://localhost:8000/scenarios", userInfo);
        // Expecting a plain string with 5 numbered scenarios. You can split it.
        const list = res.data.scenarios.split(/\n[0-9]\.?\s+/).filter(Boolean);
        setScenarios(list);
      } catch (err) {
        console.error("Failed to fetch scenarios:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchScenarios();
  }, [userInfo, scenarios, setScenarios]);

  const handleSelect = (scenario) => {
    setSelectedScenario(scenario);
    navigate("/chat");
  };

  if (!userInfo) return <p>Missing user info. Please go back and fill out the form.</p>;

  return (
    <div className="container mt-5">
      <h2 className="mb-4">🧠 GPT가 제안한 맞춤형 대화 시나리오</h2>
      {loading ? (
        <p>시나리오를 생성 중입니다... ⏳</p>
      ) : (
        <div className="list-group">
          {scenarios.map((scenario, idx) => (
            <button
              key={idx}
              className="list-group-item list-group-item-action"
              onClick={() => handleSelect(scenario)}
            >
              {scenario}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScenarioScreen;