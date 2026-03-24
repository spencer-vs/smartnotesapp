import React from 'react'
import { useEffect, useState } from 'react'
import api from "../api/axios"
import styles from "./NoteCreate.module.css"
import { useNavigate } from 'react-router-dom'
import Header from '../ui/Header'
import Footer from '../ui/Footer'
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"


const NoteCreate = () => {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const backgrounds = [bg1, bg2, bg3, bg4]
  const [index, setIndex] = useState(0)
    
    
      useEffect(() => {
        const interval = setInterval(() => {
        setIndex((prev) => (prev + 1) % backgrounds.length);
        }, 4000);
        return () => clearInterval(interval);
        }, []);
   
  


 const createNote = () => {
  setLoading(true)  
  if(!title.trim() || !content.trim()){
      alert("Title and content are required")
      return
    }
    setLoading(false)
    api.post('notes/', {
      title: title,
      content: content
    })
    .then(res => {
      setLoading(true)
      setTitle('')
      setContent('')
      alert('Note created successfully')
      navigate('/')
      setLoading(false)
    })
    .catch(err => {
      console.error('Failed to create note:', err)
      setLoading(false)
    })
   
  }

  

  




  return (
    <div>
         <Header /> 
         <div className={styles.createContainer} style={{ backgroundImage: `url(${backgrounds[index]})`}}>
          {loading && <div className={styles.loader}></div>}
        
        <textarea
          type="text"
          className={styles.createTitle}
          placeholder="Write Your Title Here"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
         
         ></textarea>


        <textarea
          type="text"
          className={styles.createText}
          placeholder="Write Your Notes Here"
          value={content}
          onChange={(e) => setContent(e.target.value)}
         
         ></textarea>
        <button className={styles.createBtn} onClick={createNote}>
          Create
        </button>
      </div>
      <Footer />
    </div>
  )
}

export default NoteCreate