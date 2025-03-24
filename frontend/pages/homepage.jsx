import React from "react";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="d-flex flex-column align-items-center justify-content-center vh-100 text-center">
      <h1 className="mb-4">맞춤형 한국어 회화 챗봇</h1>
      <button className="btn btn-primary btn-lg" onClick={() => navigate("/questionnaire")}>
        시작하기
      </button>
    </div>
  );
};

export default HomePage;