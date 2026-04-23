import LHeader from "./LHeader"
import styles from "./CreateL.module.css"
import Footer from '../ui/Footer'
import React, { useState, useRef } from "react";
import { useNavigate } from 'react-router-dom'
const CreateL = () => {
  const [recording, setRecording] = useState(false);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const mimeTypeRef = useRef("audio/webm")
  const navigate = useNavigate();
  const [paused, setPaused] = useState(false)
  const [hasRecording, setHasRecording] = useState(false)
  





  const checkStatus = (lectureId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`https://smartnoteapi.onrender.com/api/notes/lectures/${lectureId}/status/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
        });
        const data = await res.json();
        console.log("Status:", data.status);
        if (data.status === "completed") {
          clearInterval(interval);
          setLoading(false)
          navigate(`/viewlecture/${lectureId}`);
        }
        if (data.status === "failed") {
          alert("Processing failed");
          clearInterval(interval);
        }
       
      } catch (err) {
        console.error("Polling error:", err);
        clearInterval(interval);
      }
    }, 3000);
  };



  const handleRecordClick = async () => {
  
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    alert("Recording not supported on this device/browser");
    return;
  }
  
  if (!recording) {
    
    const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4"
    mimeTypeRef.current = mimeType;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream, { mimeType });
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };
    mediaRecorder.start();
    setRecording(true);
    setPaused(false);
  } else if (!paused) {
    
    mediaRecorderRef.current.pause();
    setPaused(true);
  } else {
    
    mediaRecorderRef.current.resume();
    setPaused(false);
  }
};
const handleStop = () => {
  if (mediaRecorderRef.current) {
    mediaRecorderRef.current.stop();
    setRecording(false);
    setPaused(false);
    setHasRecording(true);
  }
};
const handleSubmit = async () => {
  
  if (audioChunksRef.current.length === 0) {
    alert("No recording available");
    return;
  }
  setLoading(true)
  
  const audioBlob = new Blob(audioChunksRef.current, {
    type: mimeTypeRef.current,
  });
  const formData = new FormData();
  formData.append("audio", audioBlob, "lecture.webm");
  try {
    const token = localStorage.getItem("access");
    const response = await fetch("https://smartnoteapi.onrender.com/api/notes/upload-audio/", {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
     if(!response.ok) {
          throw new Error("Upload failed");
    }
    const data = await response.json();
    const lectureId = data.lecture_id;

    if (!lectureId) {
      alert("No lecture ID returned")
      setLoading(false);
    }
    
    checkStatus(lectureId)
  } catch (err) {
    console.error(err);
    setLoading(false);
  }
};
 
// if (handleSubmit) {
//   <div className={styles.loader}></div>
// }


  return (
    <>
      <div className={styles.create_con}>
        <LHeader />
        <div className={styles.create}>
          <div className={styles.message}>
            <p className={styles.text}>
              Click the start button to record your lectures and turn them into lecture notes using AI
            </p>
            <div className={`${styles.record} ${recording ? styles.animate : ""}`}>
              <span></span>
            </div>
            
            <div className={styles.btn}>
  {/* 🔥 Start / Pause / Resume */}
  <button onClick={handleRecordClick} className={styles.deleteBtn}>
    {!recording ? "Start" : paused ? "Resume" : "Pause"}
  </button>
  {/* ⏹ Stop */}
  {recording && (
    <button onClick={handleStop} className={styles.deleteBtn}>
      Stop
    </button>
  )}
  {/* 📤 Submit */}
  {!recording && hasRecording && (
    <button onClick={handleSubmit} className={styles.deleteBtn}>
      Submit
    </button>
  )}
 
  {loading && (
   
    <>
    <div className={styles.loader}></div>
    </>
    
  )}
  
</div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};
export default CreateL;















