import React, { useEffect, useState } from 'react'
import LHeader from './LHeader';
import Footer from '../ui/Footer';
import styles from "./ViewL.module.css"
import api from '../api/axios';
import { useParams } from 'react-router-dom';


const ViewL = () => {
  const [lecture, setLecture] = useState(null);
  const [loading, setLoading] = useState(false);
  const { id } = useParams()


  useEffect(() => {
    if (!id) return;

    setLoading(true);
    api.get(`/notes/lectures/${id}/`)
    .then(res => {
      console.log("Lecture:", res.data)
      setLecture(res.data);
      setLoading(false);
    })
    .catch(err => {
        console.error('Error fetching task:', err);
      setLoading(false);
    })
  }, [id])
  

  const deleteLectures = async (id) => {
     if(!window.confirm("Are you sure you want to delete this lecture.")) {
      return
    }

    api.delete(`notes/lectures/${id}/delete/`)
    .then(() => {
      setLecture(prev => prev.filter(lecture => lecture.id !== id))
      navigate("/lecturesnotes")
    })
    .catch(error => {
      console.error('Error deleting note:', error)
    })
  }

  const shareLectures = async (lecture) => {
    console.log("Sharing Lectures:", lecture)
    if (!lecture) return;

     const content = `${lecture.lecture || "No lecture"}`;

  const file = new File( [content],
  `${(lecture.lecture || "note").replace(/\s+/g, "_")}.txt`,
    { type: "text/plain" }
  );
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        lecture: lecture.lecture,
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
  }
  
  
  return (
    <>
    <div className={styles.view_con}>
      <LHeader />

      <div className={styles.lecture}>
       {loading ? (
         <div className={styles.loader}></div>
       ) : lecture ? (
        <>
        <textarea 
        className={styles.text}
        value={lecture.lecture}
        readOnly
        />

        <div className={styles.buttons}>
        <button className={styles.deleteBtn} onClick={deleteLectures}>
            Delete
        </button>
        <button className={styles.shareBtn} onClick={shareLectures}>
            Share
        </button>
        </div>
        </>

        
       ): (
        <p style={{ color: 'white', fontSize: '2rem'}}>No Lecture Found</p>
       )}

      

        
      </div>
      </div>
    <Footer />
    </>
  )
}

export default ViewL