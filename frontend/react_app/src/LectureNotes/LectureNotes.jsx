import React from 'react'
import LHeader from "./LHeader"
import styles from "./LectureNotes.module.css"
import { NavLink } from 'react-router-dom'
import { GrAdd } from "react-icons/gr";
import { FaSearch } from "react-icons/fa"
import Footer from '../ui/Footer'


const LectureNotes = () => {
  
  
  
  
  
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
                        <p>
                            Lorem ipsum dolor sit amet consectetur adipisicing elit. Enim repellendus odit quae temporibus, quo vel.
                        </p>
                        <p>30th-03-2026</p>

                        <button className={styles.deleteBtn}>
                            Delete
                        </button>

                        <button className={styles.shareBtn}>
                            Share
                        </button>
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