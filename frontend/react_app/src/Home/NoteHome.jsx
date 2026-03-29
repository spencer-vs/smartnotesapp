import React from 'react'
import styles from "./NoteHome.module.css"
import NHeader from './NHeader'
import Footer from '../ui/Footer'
import { useState, useEffect, useContext } from 'react'
import api from "../api/axios"
import { Link, useNavigate } from 'react-router-dom'
import { GrAdd } from "react-icons/gr";
import { Navigate } from 'react-router-dom'
import Carousels from '../ui/Carousels'
import Animation from '../ui/Animation'
import { AuthContext } from "../context/AuthContext"
import { FaSearch } from "react-icons/fa"
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"







const NoteHome = () => {

  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate()

  const { auth } = useContext(AuthContext);
 

  const backgrounds = [bg1, bg2, bg3, bg4]
  const [index, setIndex] = useState(0)
  
  
    useEffect(() => {
      const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % backgrounds.length);
      }, 4000);
      return () => clearInterval(interval);
      }, []);
 

  useEffect(() => {
    if (!auth.isAuthenticated) return;
   
    setLoading(true);

    api.get("notes/")
    .then(res => {
      setNotes(Array.isArray(res.data) ? res.data : []);
      setLoading(false);
    })

    .catch(() => {
      setNotes([])
      setLoading(false)
    })
  }, [auth])


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
  console.log("Sharing note:", note);
  if (!note) return;

  const content = `${note.title || "No Title"}\n\n${note.content || "No Content"}`;

  const file = new File( [content],
  `${(note.title || "note").replace(/\s+/g, "_")}.txt`,
    { type: "text/plain" }
  );
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        title: note.title,
        text: note.content,
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

  // if (auth.loading) {
  //   return <AuthSpinner />
  // }

  if (!auth.isAuthenticated) {
    return (
      <div>
        <Animation />
      </div>
    )
  }

   return (
    <div>
     
        <NHeader /> 


      

      <div className={styles.noteContainer}>
        {loading && <div className={styles.loader}></div>}
        {auth.isAuthenticated ? (
          <>
          <div className={styles.searchIcon}>
             <Link className={styles.icon} to="/SearchNotes">
              <FaSearch />
             </Link>
          </div>
          
          <div className={styles.createIcon}>
             <Link className={styles.icon} to="/create">
              <GrAdd />
             </Link>
          </div>
          </>
        ) : (
           <Animation />
        )}
       
       
       {auth.isAuthenticated && (

       
        <ul className={styles.listDisplay}>
          {notes.map(note => (
            <li className={styles.noteList} key={note.id}>
              <Link className={styles.noteLink} to={`/notes/${note.id}/update`}>
                <h2 className={styles.noteTitle}>{note.title}</h2>
                <p className={styles.noteText}>{note.content}</p>
                <div className={styles.noteBtn}>
                    <button onClick={() => handleDelete(note.id)} className={styles.updateNote}>
                   Delete
              </button>
              
              <button className={styles.updateNote} onClick={() => navigate(`/notes/${note.id}/update`)}>
                Update
              </button>
              
              <button className={styles.updateNote} onClick={() => handleShare(note)}>
                Share
              </button>

              
              
                </div>
               
              </Link>
               
            </li>
          ))}
        </ul> 
        )}
      </div>
      <Footer />
    </div>
  )
}

export default NoteHome


