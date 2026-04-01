import React from 'react'
import LHeader from "./LHeader"
import styles from "./LectureNotes.module.css"
import { NavLink } from 'react-router-dom'
import { GrAdd } from "react-icons/gr";
import { FaSearch } from "react-icons/fa"
import Footer from '../ui/Footer'
import { useState, useEffect } from 'react';
import {useNavigate,  } from 'react-router-dom'
import api from '../api/axios';


const LectureNotes = () => {
  const [lectures, setLectures] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate()
  
   
  

  useEffect(() => {
          setLoading(true)
          api.get('notes/lectures/')
          .then(res => {
              setLoading(true)
              console.log("Lectures:", res.data)
              setLectures(res.data)
              setLoading(false)
          })
          .catch(err => {
              console.log("Failed to fetch task:", err.message)
              setLoading(false)
          })
      }, [])
    
  


   const truncateWords = (text, limit) => {
    if (!text) return "";
    const words = text.split(" ");
    return words.length > limit
    ? words.slice(0, limit).join(" ") + "..."
    : text;
    };
  
  
  
    return (
   <>
   <div className={styles.lecture_con}>
        <LHeader />

         <div className={styles.icons}>
           <div className={styles.search}>
            <NavLink className={styles.icon} to="/createlecture">
               <FaSearch />
            </NavLink>
           </div>
         
           <div className={styles.add}>
            <NavLink className={styles.icon} to="/createlecture">
              <GrAdd />
            </NavLink>
           </div>
          </div>

        <div className={styles.lecture}>
           
            <h1 className={styles.heading}>Lecture Notes</h1>

            <div className={styles.all_lecture}>
                <ul className={styles.lecture_list}>
                 <li className={styles.list}>
               <NavLink className={styles.link}>
                 {lectures.length === 0 ? (
                     <p className={styles.task_no}>Loading Lectures</p>
                 )
                    : (
                            lectures.map(lecture => (
                                <div className={styles.task_display} key={lecture.id}>
                                 <p className={styles.display_title}>{lecture.created_at}</p>
                                 <p className={styles.display_list}>{truncateWords(lecture.lecture, 10)}</p>
                    
                                 <button className={styles.deleteBtn}>
                            Delete
                        </button>

                        <button className={styles.shareBtn}>
                            Share
                        </button>
                                </div>
                            ))
                        )}
                </NavLink>
                </li>

                </ul>

            </div>
        </div>
        
    </div>
    <Footer />
    </>

  )
}

export default LectureNotes