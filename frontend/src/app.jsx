import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import QuestionnairePage from "./pages/QuestionnairePage";
import ChatbotPage from "./pages/ChatbotPage";
import { UserProvider } from "./context/UserContext";
import "bootstrap/dist/css/bootstrap.min.css";
import ScenarioScreen from "./pages/ScenarioScreen";

function App() {
  return (
    <UserProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/questionnaire" element={<QuestionnairePage />} />
          <Route path="/scenarios" element={<ScenarioScreen />} /> {/* NEW */}
          <Route path="/chat" element={<ChatbotPage />} />
        </Routes>
      </Router>
    </UserProvider>
  );
}

export default App;
