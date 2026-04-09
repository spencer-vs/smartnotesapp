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
        <button className={styles.deleteBtn}>
            Delete
        </button>
        <button className={styles.shareBtn}>
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