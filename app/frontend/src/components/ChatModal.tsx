import React, { useState } from "react";
import {
  Modal,
  Box,
  TextField,
  Button,
  CircularProgress,
  SxProps,
  Theme,
} from "@mui/material";

import ChatMessage from "./ChatMessage";

interface ChatModalProps {
  open: boolean;
  handleClose: () => void;
  conversationId: string;
}

const ChatModal: React.FC<ChatModalProps> = ({
  open,
  handleClose,
  conversationId,
}) => {
  const [message, setMessage] = useState<string>("");
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    setIsLoading(true);
    const apiUrl = `http://localhost:8000/conversation/${conversationId}`;
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: message }),
      });
      const data = await response.json();
      if (response.ok) {
        setChatHistory(data.response);
        setMessage("");
      } else {
        console.error("Error fetching data:", data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
    setIsLoading(false);
  };

  const modalStyle: SxProps<Theme> = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 400,
    bgcolor: "background.paper",
    boxShadow: 24,
    p: 4,
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="chat-modal"
      aria-describedby="chat-modal-for-sending-messages"
    >
      <Box sx={modalStyle}>
        <Box sx={{ maxHeight: 300, overflow: "auto", mb: 2 }}>
          {chatHistory.map((msg, index) => (
            <ChatMessage
              key={index}
              isUser={msg.role === "human"}
              text={msg.content}
            />
          ))}
        </Box>
        <TextField
          label="Type your message"
          fullWidth
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          variant="outlined"
          margin="normal"
          disabled={isLoading}
        />
        {isLoading ? (
          <CircularProgress
            size={24}
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              marginTop: "-12px",
              marginLeft: "-12px",
            }}
          />
        ) : (
          <Button variant="contained" color="primary" onClick={handleSend}>
            Send
          </Button>
        )}
      </Box>
    </Modal>
  );
};

export default ChatModal;
