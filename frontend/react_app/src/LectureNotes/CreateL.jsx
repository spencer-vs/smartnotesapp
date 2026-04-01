
import LHeader from "./LHeader"
import styles from "./CreateL.module.css"
import { NavLink } from 'react-router-dom'
import Footer from '../ui/Footer'
import React, { useState, useRef } from "react";



const CreateL = () => {
  
//  const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [date, setDate] = useState(new Date());


    useEffect(() => {
        const timer = setInterval(() => {
         setDate(new Date());
        }, 1000)

        return () => clearInterval(timer);
    }, [])
   
  
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      mediaRecorder.start();
      setRecording(true);
      console.log("Recording started...");
    } catch (err) {
      console.error("Microphone error:", err);
    }
  };
  const stopRecording = async () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
    setLoading(true)
    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      try {
        const token = localStorage.getItem("access");
        const response = await fetch("http://127.0.0.1:8000/api/notes/upload-audio/", {
          method: "POST",
          body: formData,
          headers: {
            Authorization: `Bearer ${token}`
          },
        });
        const data = await response.json();
        console.log("Upload response:", data);
        setNotes(data.lecture_notes)
      } catch (error) {
        console.error("Upload error:", error);
      } finally {
        setLoading(false);
      }
    };
    console.log("Recording stopped...");
  };
  
  
  
  
  
  
  
  
  
  return (
    
  <>
    <div className={styles.create_con}>
     <LHeader />

    <div className={styles.create}>
     <div className={styles.message}>
       <p className={styles.text}>
        Click the start button to record your lectures and turn them into lecture notes using AI
       </p>
       
       <div className={`${styles.record} ${recording ? styles.animate : ""}`}><span></span></div>
       
       <div className={styles.btn}>
        {!recording ? (
       <button className={styles.deleteBtn} onClick={startRecording}>Start</button>
      ) : (
        <button className={styles.shareBtn} onClick={stopRecording}>Stop</button>
      )}

      {loading && <p style={{ color: "white"}}>Generating notes...</p>}

     
      </div>
     </div>
      {notes && (
        <div style={{ marginTop: "20px"}}>
          <h3>Lecture Notes</h3>
          <pre style={{ whiteSpace: "pre-wrap", color: "white"}}>{notes}</pre>
          <p className={styles.date}>{date.toLocaleDateString()}</p>
        </div>
      )}
       
    </div>

    
    </div>
    <Footer />
  </> 
  )
}

export default CreateL