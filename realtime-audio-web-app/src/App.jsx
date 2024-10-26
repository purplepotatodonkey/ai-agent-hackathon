import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [ws, setWs] = useState(null);
  const url = `ws://localhost:8081`;

  useEffect(() => {
    const apiKey = import.meta.env.OPENAI_API_KEY;
    // const url = `wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01?authorization=Bearer ${apiKey}?openai-beta=realtime=v1`;
    
    const socket = new WebSocket(url);

    socket.addEventListener("open", function open() {
        console.log("Connected to server.");
        socket.send(JSON.stringify({
            type: "response.create",
            response: {
                modalities: ["text"],
                instructions: "Please assist the user.",
            }
        }));
    });

    socket.addEventListener("message", function incoming(message) {
        console.log(JSON.parse(message.data));
    });

    setWs(socket);

    return () => {
      socket.close();
    };
  }, [])

  const clientRef = useRef(new RealtimeClient(url));

  const wavRecorderRef = useRef(
    new WavRecorder({ sampleRate: 24000 })
  );
  const wavStreamPlayerRef = useRef(
    new WavStreamPlayer({ sampleRate: 24000 })
  );
  
  return (
    <>
    </>
  )
}

export default App
