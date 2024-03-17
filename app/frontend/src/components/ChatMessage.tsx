import React from "react";
import chefImage from "../assets/chef.jpg";
import userImage from "../assets/user.jpg";

interface ChatMessageProps {
  isUser: boolean;
  text: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ isUser, text }) => {
  const chatStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "row", // Align items in a row
    justifyContent: isUser ? "flex-end" : "flex-start",
    alignItems: "center", // Vertically center align items
    marginBottom: "10px",
  };

  const imageStyle: React.CSSProperties = {
    borderRadius: "50%",
    width: "50px",
    height: "50px",
    objectFit: "cover",
    margin: "0 10px",
  };

  const textStyle: React.CSSProperties = {
    maxWidth: "70%",
    padding: "10px",
    borderRadius: "15px",
    backgroundColor: isUser ? "darkblue" : "grey",
    color: "white",
  };

  return (
    <div style={chatStyle}>
      {!isUser && <img src={chefImage} alt="AI" style={imageStyle} />}
      <div style={textStyle}>{text}</div>
      {isUser && <img src={userImage} alt="User" style={imageStyle} />}
    </div>
  );
};

export default ChatMessage;
