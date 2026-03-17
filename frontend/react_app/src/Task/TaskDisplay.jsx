import React from 'react'
import styles from './TaskDisplay.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'

const SavedTask = () => {
  return (
   <>
    
   <div className={styles.display_con}>
    <Header />
    
           <div className={styles.display_task}>
                 <h1 className={styles.display_title}>
                  Lectures
                 </h1>

                 <p className={styles.display_content}>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. Laudantium facilis aspernatur mollitia ipsa sequi quod a temporibus dolorem, nostrum consequuntur explicabo? Modi soluta facere eligendi dicta corporis ut nostrum esse.
                 </p>
           </div>
    </div>
    <Footer />
    </>
  )
}

export default SavedTask