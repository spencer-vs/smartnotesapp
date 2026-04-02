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
              // console.log("Lectures:", res.data)
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

   <div className={styles.lecture_con}>
        <LHeader />

         <div className={styles.icons}>
           <div className={styles.search}>
            <NavLink className={styles.icon} to="/">
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

            
                 {lectures.length === 0 ? (
                        <div className={styles.loader}></div>
                 )
                    : (  
                    <div className={styles.all_lecture}>
                    {lectures.map(lecture => (
                                <div className={styles.all_lecture} key={lecture.id}>
                                 <ul className={styles.lecture_list}>
                                 <NavLink className={styles.link} to={`/viewlecture/${lecture.id}/`}>
                                 <li className={styles.list}>
                                 <p className={styles.date}>{lecture.created_at}</p>
                                 <p className={styles.truncate}>{truncateWords(lecture.lecture, 10)}</p>
                                 <button className={styles.deleteBtn}>
                                  Delete
                                 </button>
                               <button className={styles.shareBtn}>
                            Share
                        </button>
                        
                        </li>
                         </NavLink>
                        </ul>
                         </div> 
                         ))}
                    </div>
                    )}
               
                  
              
              
            </div>
            <Footer />
            </div>
           
        
        
    

  )
}

export default LectureNotes