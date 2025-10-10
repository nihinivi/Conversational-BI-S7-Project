import React from 'react';
import './ChatInterface.css';
import { useState,useEffect ,useRef} from "react";

import { BounceLoader } from 'react-spinners';


const Server="http://localhost:5000/"



const UploadButton = ({ setFile }) => {
  const fileInputRef = useRef(null);

  const handleUploadClick = () => fileInputRef.current.click();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);   
      console.log("Selected file:", selectedFile);
    }
  };

  return (
    <>
      <div onClick={handleUploadClick} className="cursor-target button-placeholder cursor-pointer">
        Upload Dataset
      </div>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
    </>
  );
};






const ChatInputBar = ({setLoading,setData}) => {

const handleSend = async () => {
  
  if (!query || !file) return alert("Enter query or upload a file");
setLoading(1)
  const formData = new FormData();
  formData.append("query", query);
  if (file) formData.append("file", file);

  try {
    const res = await fetch(Server+"api/data", {
      method: "POST",
      body: formData,
    });
    const result = await res.json();
    setData({url:result.image_url , title:result.query}) 
    
    setQuery("");
    setFile(null);
  } catch (err) {
    console.error(err);
  }
  setLoading(0)
};
 
  const [query, setQuery] = useState(""); 
  const [file, setFile] = useState(null);



  return (
    <div className="chat-input-bar">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Type your query here..."
        className="input-field-placeholder  cursor-target"
      /> 
     <UploadButton setFile={setFile} />
  <div onClick={handleSend} className="button-placeholder cursor-target send-button cursor-pointer">
  Send
</div>
    </div>
  );
}; 
const ChatDisplayArea = ({ isLoading, data }) => {
  return (
    <div className="chat-display-area p-6 flex flex-col w-screern h-screen">
      <div className=" h-screen w-full flex items-center justify-center p-5 rounded-xl   flex-1 min-h-0">
        {isLoading ? (
          <BounceLoader />
        ) : !data?.url ? (
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-24 h-24"
          >
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
        ) : ( 
            <img
              className="w-full max-h-[90vh] cursor-target rounded-4xl border-20 border-[#322e3a] object-contain"
              src={data.url}
              alt={data.title || "img"}
            /> 
        )}
      </div>

      <div className="bg-[#4b4948] w-full rounded-xl py-2 px-4 mt-6">
        <p className="text-white">{data?.title}</p>
      </div>
    </div>
  );
};
 


const HistoryCard = ({ date, title, setActive, active,id ,setChat}) => {
  
  const handleClick = async () => {  
    setActive(id);
    try {
      const res = await fetch(`${Server}/api/log?id=${id}`);
      const data = await res.json();
      setChat({ url: data.url, title: data.title });
    } catch (err) {
      console.error("Error fetching chat:", err);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`flex flex-col cursor-target justify-between p-3 rounded-xl cursor-pointer transition-all duration-200 border 
        ${
          active==id
            ? "bg-gradient-to-r from-blue-600 to-blue-800 text-white border-transparent shadow-lg"
            : "bg-gray-800 hover:bg-gray-700 border-gray-700 text-gray-200"
        }`}
    > 
      <div className="text-xs text-gray-400 mb-1">{date}</div>
 
      <div className="font-medium text-sm truncate">{title}</div>
    </div>
  );
};
 

const ChatHistorySidebar = ({setChat}) => {
  const [active,setActive]=useState(0)
  const [chats,setChats]=useState([])
  
  const fetchChats = async () => {
    try {
      const res = await fetch(Server + "/api/history");
      const data = await res.json();
      setChats(data.history);
      console.log(data.history)
    } catch (err) {
      console.error("Error fetching chats:", err);
    }
  };
useEffect(() => {
  fetchChats();
}, []); 


  return (
    <aside className="chat-history-sidebar">
      <div className="sidebar-header">
        <h3>Chat History</h3> 
      </div>
      <div className="chat-history-list">
      
        <div className="chat-history-list flex flex-col gap-2">
        <HistoryCard  date="Current" setActive={setActive} setChat={setChat} active={active} id={0} title="" />



      
      {chats.map((chatTimestamp, index) => (
  <HistoryCard 
    key={chatTimestamp}
    id={chatTimestamp}
   date={new Date(chatTimestamp*1000).toLocaleDateString("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
})}
    title={`Chat ${index + 1}`}
    setActive={setActive}
    active={active}
    setChat={setChat} 
  />
))} 

      </div>
      </div>
      <div className="new-chat-button-placeholder cursor-target" onClick={()=>{
        fetchChats()
        setActive(0)
        setChat({url:"",title:""})
      }} >+ New Chat</div>

    </aside>
  );
};
 

const ChatInterface = () => {

  const [isLoading,setload]=useState(0);

  const [data, setData] = useState({ url: "", title: "" });

  return (
    <div className="chat-interface-container ">
      <main className="main-content">
        <ChatInputBar setLoading={setload} setData={setData} />
        <ChatDisplayArea isLoading={isLoading} data={data}/>
      </main> 
      <ChatHistorySidebar setChat={setData}/>
      </div>
  );
};

export default ChatInterface;