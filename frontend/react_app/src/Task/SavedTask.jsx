import React from 'react'
import styles from './SavedTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'

const SavedTask = () => {
  return (
   <>
    
   <div className={styles.save_cont}>
    <Header />
    
            <h1 className={styles.saved_header}>Saved TimeTable</h1>
           
        <div className={styles.saved_task}>
            <NavLink className={styles.task}>
                <div className={styles.task_title}>Lectures</div>
            </NavLink>

             <NavLink className={styles.task}>
                <div className={styles.task_title}>Lectures</div>
            </NavLink>


             <NavLink className={styles.task}>
                <div className={styles.task_title}>Lectures</div>
            </NavLink>
           
            

        </div>
        
    </div>
    <Footer />
    </>
  )
}

export default SavedTask