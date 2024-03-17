import React, { useState } from "react";
import ChatModal from "./components/ChatModal";
import IconButton from "@mui/material/IconButton";
import Avatar from "@mui/material/Avatar";
import chefIcon from "./assets/chef.jpg"; // Make sure the path is correct

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
      <div className="intro-container">
        <h1>Welcome to Chef Amico's Italian Kitchen</h1>
        <p>
          Join us for an authentic Italian dining experience. Our chatbot is
          ready to assist with recommendations and answer any questions you may
          have.
        </p>
      </div>
      <IconButton
        onClick={handleOpenModal}
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          backgroundColor: "#fff",
          borderRadius: "50%",
          width: "150px",
          height: "150px",
          padding: 0,
        }}
      >
        <Avatar
          src={chefIcon}
          alt="Open Chat"
          style={{
            width: "150px",
            height: "150px",
          }}
        />
      </IconButton>
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
