import React from "react";
import { useUser } from "../context/UserContext";

const ChatbotPage = () => {
  const { userInfo } = useUser();

  return (
    <div className="container mt-5">
      <h2>💬 Chatbot</h2>
      {userInfo ? (
        <pre>{JSON.stringify(userInfo, null, 2)}</pre>
      ) : (
        <p>No user info found.</p>
      )}
    </div>
  );
};

export default ChatbotPage;