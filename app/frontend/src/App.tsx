import React, { useState } from "react";
import ChatModal from "./components/ChatModal";

import "./App.css";

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [conversationId, setConversationId] = useState("");

  const handleOpenModal = async () => {
    try {
      const response = await fetch("http://localhost:8000/start_conversation", {
        method: "POST",
      });
      const data = await response.json();
      if (response.ok) {
        setConversationId(data.conversation_id);
        console.log("Received conversation ID:", data.conversation_id);
        setIsModalOpen(true);
      } else {
        console.error("Error fetching conversation ID:", data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="App">
      <div className="background"></div>

      <button onClick={handleOpenModal}>Open Chat</button>

      {isModalOpen && (
        <ChatModal
          open={isModalOpen}
          handleClose={handleCloseModal}
          conversationId={conversationId}
        />
      )}
    </div>
  );
}

export default App;
