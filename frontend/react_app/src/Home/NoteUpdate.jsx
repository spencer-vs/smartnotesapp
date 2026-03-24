import React from 'react'
import styles from './NoteUpdate.module.css'
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from "../api/axios"
import Header from '../ui/Header';
import Footer from '../ui/Footer';
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"

const NoteUpdate = () => {
 
   

  const { id } = useParams()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const backgrounds = [bg1, bg2, bg3, bg4]
    const [index, setIndex] = useState(0)
      
      
        useEffect(() => {
          const interval = setInterval(() => {
          setIndex((prev) => (prev + 1) % backgrounds.length);
          }, 4000);
          return () => clearInterval(interval);
          }, []);
     
  
  useEffect(() => {
    api.get(`notes/${id}/`)
    .then(res => {
      setLoading(true)
     setTitle(res.data.title)
     setContent(res.data.content)
     setLoading(false)
    })
    .catch(err => {
        console.error('Failed to fetch note:', err)
        setLoading(false)
    })
  }, [id])


  const handleUpdate = () => {
  api.put(`notes/${id}/update/`, {
    title,
    content
  })
  .then(() => {
    alert('Note updated successfully')
    navigate('/')
  })
  .catch(err => {
    console.error('Failed to update note:', err)
  })
}
  
  
  
  
  return (
   <>
   <Header /> 
  
   <div className={styles.updateContainer} style={{ backgroundImage: `url(${backgrounds[index]})`}}>
      {loading && <div className={styles.loader}></div>}
        <textarea 
        value={title}
        className={styles.updateTitle}
        onChange={(e) => setTitle(e.target.value)}
        placeholder='Title'
        />

        <textarea 
        value={content}
        className={styles.updateContent}
        onChange={(e) => setContent(e.target.value)}
        />
    
        <button className={styles.updateBtn} onClick={handleUpdate}>
          Update  
        </button>
    </div>
    <Footer />
     </>
  );

}

  

export default NoteUpdate