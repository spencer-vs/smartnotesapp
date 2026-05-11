import React, { useEffect, useState } from 'react'
import LHeader from './LHeader';
import Footer from '../ui/Footer';
import styles from "./ViewL.module.css"
import api from '../api/axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useRef } from "react";


const ViewL = () => {
  const [lecture, setLecture] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetched, setFetched] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();
   

  
 useEffect(() => {
  if (!id) return;
  setLoading(true);
  api.get(`/notes/lectures/${id}/`)
    .then(res => {
      console.log("Lecture:", res.data);
      setLecture(res.data);
      setLoading(false);
      setFetched(true); // ✅ important
    })
    .catch(err => {
      console.error("Error fetching lecture:", err);
      setLoading(false);
      setFetched(true); // ✅ even on error
    });
}, [id]);


  // ✅ FIX 2: DELETE (correct usage)
  const deleteLectures = async (id) => {
    if (!window.confirm("Are you sure you want to delete this lecture?")) return;
    try {
      await api.delete(`notes/lectures/${id}/delete/`);
      setLecture(null);
      navigate("/lecturenotes");
    } catch (error) {
      console.error('Error deleting lecture:', error);
    }
  };
  
  
  

  const shareLectures = async (lecture) => {
  if (!lecture) return;
  const shareText = lecture.lecture || "No Lecture Content";
  const file = new File(
    [shareText],
    `Lecture_Note.txt`,
    { type: "text/plain" }
  );
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        title: "Lecture Notes",
        text: shareText,
        files: [file],
      });
    } catch {
      console.log("Share cancelled");
    }
  } else {
    const blobUrl = URL.createObjectURL(file);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = file.name;
    a.click();
      URL.revokeObjectURL(blobUrl);
  }
};


  return (
    <>
      <div className={styles.view_con}>
        <LHeader />
        <div className={styles.lecture}>
        
               {loading ? (
  <div className={styles.loader}></div>
) : !lecture || !lecture.lecture ? (
  <p style={{ color: 'white', fontSize: '2rem' }}>
    No Lecture Found
  </p>
) : (
  <>
    <textarea
      className={styles.text}
      value={lecture.lecture}
      readOnly
    />
    <div className={styles.buttons}>
      <button
        className={styles.deleteBtn}
        onClick={() => deleteLectures(lecture.id)}
      >
        Delete
      </button>
      <button
        className={styles.shareBtn}
        onClick={() => shareLectures(lecture)}
      >
        Share
      </button>
    </div>
  </>
)}
         
        </div>
      </div>
      <Footer />
    </>
  );
};
export default ViewL;