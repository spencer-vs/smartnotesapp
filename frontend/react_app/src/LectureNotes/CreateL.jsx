
import LHeader from "./LHeader"
import styles from "./CreateL.module.css"
import { NavLink } from 'react-router-dom'
import Footer from '../ui/Footer'
import React, { useState, useRef } from "react";



const CreateL = () => {
  
//  const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  
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
    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      try {
        const response = await fetch("http://127.0.0.1:8000/api/notes/upload-audio/", {
          method: "POST",
          body: formData,
        });
        const data = await response.json();
        console.log("Upload response:", data);
      } catch (error) {
        console.error("Upload error:", error);
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
      </div>
     </div>

       
    </div>

    
    </div>
    <Footer />
  </> 
  )
}

export default CreateL