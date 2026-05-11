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


   const truncateWords = (text, limit) => {
    if (!text) return "";
    const words = text.split(" ");
    return words.length > limit
    ? words.slice(0, limit).join(" ") + "..."
    : text;
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
                <p className={styles.noteText}>
                  {truncateWords(note.content, 15)}
                </p>
               
               <div className={styles.noteBtn}>
              {/* <button className={styles.updateNote} onClick={() => navigate(`/notes/${note.id}/update`)}>
                Update
              </button>
              
             */}

              
              
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


