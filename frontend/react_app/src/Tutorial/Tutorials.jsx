import React from 'react'
import { useState } from 'react'
import styles from "./Tutorials.module.css"
import THeader from './THeader'
import Footer from '../ui/Footer'
import { GrAdd } from "react-icons/gr";
import { FaSearch } from "react-icons/fa"
import { NavLink } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import api from "../api/axios"

const Tutorials = () => {
   
   const [tutorials, setTutorials] = useState([])
   const [loading, setLoading] = useState(false)
   const navigate = useNavigate()
    
   
   
   const truncateWords = (text, limit) => {
    if (!text) return "";
    const words = text.split(" ");
    return words.length > limit
    ? words.slice(0, limit).join(" ") + "..."
    : text;
    };

    
    useEffect(() => {
        setLoading(true)
        api.get('notes/tutorials/')
        .then(res => {
            setLoading(true)
            console.log("Tutorials:", res.data)
            setTutorials(res.data)
            setLoading(false)
        })
        .catch(err => {
            console.log("Failed to fetch tutorials:", err.message)
            setLoading(false)
        })
    }, [])
   
  
  
  
  
  
  
  
  
  
  
  
  
  
    return (
    <>
    <div className={styles.tutorials_con}>
        <THeader />
        
         <div className={styles.icons}>
           <div className={styles.search}>
            <NavLink className={styles.icon} to="/searchtutorial">
               <FaSearch />
            </NavLink>
           </div>
         
           <div className={styles.add}>
            <NavLink className={styles.icon} to="/createtutorials">
               <GrAdd />
            </NavLink>
           </div>
          </div>


    <div className={styles.tutorials}>
    <h1 className={styles.tutorial_header}>All Tutorials</h1>
          
              {tutorials.length === 0 ? (
    <p className={styles.tutorial_no}>No Tutorials Found</p>
     ) : (
   tutorials.map((tutorial) => (
    <div className={styles.tutorial_display} key={tutorial.id}>
      <h3 className={styles.display_title}>
        {tutorial.title}
      </h3>
      <p className={styles.display_list}>
        {truncateWords(tutorial.text, 10)}
      </p>
      <button
        onClick={() => navigate(`/viewtutorials/${tutorial.id}/`)}
        className={styles.display_btn}
      >
        View Tutorial
      </button>
    </div>
   
     ))
    )}
    </div>                

        
    </div>
    <Footer />
    </>
  )
}

export default Tutorials