import RoundedButton2 from "./RoundedButton2";
import { useState, useEffect } from "react";
import { Popconfirm } from "antd";  
import { useNavigate } from "react-router-dom"; 
import axios from "axios";

function LogOut() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [userChatMessages, setUserChatMessages] = useState([]);
  const [userData, setUserData] = useState([]);
  const [isLogOut, setIsLogOut] = useState(false);  // Added
  const [description, setDescription] = useState("Are you sure you want to LogOut");

  const showPopconfirm = () => {
    setOpen(true);
  };

  useEffect(() => {
    const userChat = JSON.parse(localStorage.getItem('chatMessages'));
    const user = JSON.parse(localStorage.getItem('userDetails'));
    if (userChat) {
      setUserChatMessages(userChat);
    }
    if (user) {
      setUserData(user);
    }
  }, []);

  // const convertChatDataToPairs = (chatData) => {
  //   const result = [];
  //   let userMessage = "";
  //   let botMessage = "";
  //   for (let i = 1; i < chatData.length; i++) {
  //     const entry = chatData[i];
  //     if (entry.sender === "user") {
  //       userMessage = entry.text;
  //     } else if (entry.sender === "bot") {
  //       botMessage = entry.text;
  //       if (userMessage) {
  //         result.push(`${userMessage}: ${botMessage}`);
  //         userMessage = "";
  //       }
  //     }
  //   }
  //   return result;
  // };

  const convertChatDataToPairs = (chatData) => {
    const result = [];
    let userMessage = "";
    let botMessage = "";
    
    for (let i = 1; i < chatData.length; i++) {
      const entry = chatData[i];
      
      if (entry.sender === "user") {
        userMessage = entry.text;
      } else if (entry.sender === "bot") {
        botMessage = entry.text;
        
        if (userMessage) {
          // Push a dictionary object to the result array
          result.push({
            sender: userMessage,   // User message
            bot: botMessage      // Bot message
          });
          userMessage = "";  // Reset after storing
        }
      }
    }
    
    return result;
  };
  

  const handleOk = async () => {
    const chatPairs = convertChatDataToPairs(userChatMessages);
    const logOutData = {
      email: userData.email,
      chat_history: chatPairs,
      session_id: userData.uid
    };

    setConfirmLoading(true);
    try {
      console.log(logOutData);
      const response = await axios.post("http://localhost:5000/logout", logOutData);
      // console.log(response);
      if (response.status === 201) {
        setIsLogOut(true);
        localStorage.removeItem("userDetails");
        localStorage.removeItem("chatMessages");
        setDescription("User Successfully Logged Out!");
        setTimeout(() => {
          navigate('/');
          window.location.reload();
        }, 100);
      }
    } catch (error) {
      console.error("LogOut failed: ", error);
      setDescription("LogOut failed, please try again.");
    }
    setConfirmLoading(false);
  };

  const handleCancel = () => {
    console.log('Clicked cancel button');
    setOpen(false);
  };

  return (
    <Popconfirm
      title="LogOut Confirm"
      content={description}  // Updated prop
      open={open}
      onConfirm={handleOk}
      okButtonProps={{
        loading: confirmLoading,
      }}
      onCancel={handleCancel}
    >
      <RoundedButton2 label="LogOut" onClick={showPopconfirm} style={{ backgroundColor: 'black', color: 'white' }}></RoundedButton2>
    </Popconfirm>
  );
}

export default LogOut;
