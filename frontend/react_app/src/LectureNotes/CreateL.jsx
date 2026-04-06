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
  const navigate = useNavigate();
  const [paused, setPaused] = useState(false)
  const [hasRecording, setHasRecording] = useState(false)
  





  const checkStatus = (lectureId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/notes/lectures/${lectureId}/status/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
        });
        const data = await res.json();
        console.log("Status:", data.status);
        if (data.status === "completed") {
          clearInterval(interval);
          // ✅ redirect to view page
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
  if (!recording) {
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
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
  const audioBlob = new Blob(audioChunksRef.current, {
    type: "audio/webm",
  });
  const formData = new FormData();
  formData.append("audio", audioBlob, "lecture.webm");
  try {
    const token = localStorage.getItem("access");
    const response = await fetch("http://127.0.0.1:8000/api/notes/upload-audio/", {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    const lectureId = data.lecture_id;
    if (lectureId) {
      navigate(`/viewlecture/${lectureId}`);
    }

    if (!lectureId) {
      alert("No lecture ID returned")
    }
    checkStatus(lectureId)
  } catch (err) {
    console.error(err);
  }
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

  {loading && <p style={{ color: "white" }}>Processing audio...</p>}
</div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};
export default CreateL;















{/* <div className={styles.btn}>
              {!recording ? (
                <button className={styles.deleteBtn} onClick={startRecording}>
                  Start
                </button>
              ) : (
                <button className={styles.shareBtn} onClick={stopRecording}>
                  Pause
                </button>
              )}
               <button className={styles.shareBtn} onClick={generateLecture}>
                  Submit
               </button>
              {loading && <p style={{ color: "white" }}>Processing audio...</p>}
            </div> */}


//  const startRecording = async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       const mediaRecorder = new MediaRecorder(stream);
//       mediaRecorderRef.current = mediaRecorder;
//       audioChunksRef.current = [];
//       mediaRecorder.ondataavailable = (event) => {
//         audioChunksRef.current.push(event.data);
//       };
//       mediaRecorder.start();
//       setRecording(true);
//     } catch (err) {
//       console.error("Microphone error:", err);
//     }
//   };
//   const stopRecording = async () => {
//     mediaRecorderRef.current.stop();
//     setRecording(false);
//     setLoading(true);
//     mediaRecorderRef.current.onstop = async () => {
//       const audioBlob = new Blob(audioChunksRef.current, {
//         type: "audio/webm",
//       });
//       const formData = new FormData();
//       formData.append("audio", audioBlob, "recording.webm");
     
//     };
// };



// const generateLecture = async () => {
//            try {
//         const token = localStorage.getItem("access");
//         const response = await fetch("http://127.0.0.1:8000/api/notes/upload-audio/", {
//           method: "POST",
//           body: formData,
//           headers: {
//             Authorization: `Bearer ${token}`
//           },
//         });
//         const data = await response.json();
//         console.log("Upload response:", data);
//         // ✅ FIX: get lectureId HERE
//         const lectureId = data.lecture_id;
//         if (!lectureId) {
//           alert("No lecture ID returned");
//           return;
//         }
//         // ✅ start polling
//         checkStatus(lectureId);
//       } catch (error) {
//         console.error("Upload error:", error);
//       }
//     }



