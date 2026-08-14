import React from 'react'
import styles from './NoteUpdate.module.css'
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from "../api/axios"
import Header from '../ui/Header';
import NHeader from './NHeader'
import Footer from '../ui/Footer';
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"
import { toast } from 'react-toastify';

const NoteUpdate = () => {
 
   

  const { id } = useParams()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [note, setNotes] = useState([]);
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
     setNotes(res.data)
     setLoading(false)
    })
    .catch(err => {
        console.error('Failed to fetch note:', err)
        setLoading(false)
        toast.error('Failed to fetch note')
    })
  }, [id])


  const handleUpdate = () => {
  api.put(`notes/${id}/update/`, {
    title,
    content
  })
  .then(() => {
    toast('Note updated successfully')
    navigate('/')
  })
  .catch(err => {
    console.error('Failed to update note:', err)
    toast.error('Failed to update note')
  })
}




const handleDelete = (id) => {
    if(!window.confirm("Are you sure you want to delete this note.")) {
      return
    }

    api.delete(`notes/${id}/delete/`)
    .then(() => {
      setNotes(prevNotes => prevNotes.filter(note => note.id !== id))
      navigate("/")
    })
    .catch(error => {
      console.error('Error deleting note:', error)
    })
  }

  

  const handleShare = async (note) => {
  if (!note) return;
  const shareText = `${note.title || "No Title"}\n\n${note.content || "No Content"}`;
  try {
    
    if (navigator.share) {
      await navigator.share({
        title: note.title || "Note",
        text: shareText,
      });
    } else {
      
      await navigator.clipboard.writeText(shareText);
      alert("Note copied to clipboard");
    }
  } catch (err) {
    console.log("Share cancelled", err);
  }
};
  
  return (
   <>
   <NHeader /> 
  
   <div className={styles.updateContainer}>
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

        
          <button onClick={() => handleDelete(note.id)}  className={styles.updateBtn}>
              Delete
        </button>

        <button onClick={() => handleShare({
            title,
            content
          })} className={styles.updateBtn}>
          Share
        </button>
    </div>
    <Footer />
     </>
  );

}

  

export default NoteUpdate