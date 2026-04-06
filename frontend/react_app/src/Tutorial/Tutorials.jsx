import React from 'react'
import { useState } from 'react'
import styles from "./Tutorials.module.css"
import THeader from './THeader'
import Footer from '../ui/Footer'
import { GrAdd } from "react-icons/gr";
import { FaSearch } from "react-icons/fa"
import { NavLink } from 'react-router-dom'

const Tutorials = () => {
  
  
  
  
  
  
  
  
  
  
  
    return (
    <>
    <div className={styles.tutorials_con}>
        <THeader />
        
         <div className={styles.icons}>
           <div className={styles.search}>
            <NavLink className={styles.icon} to="/createtutorials">
               <FaSearch />
            </NavLink>
           </div>
         
           <div className={styles.add}>
            <NavLink className={styles.icon} to="/createtutorials">
               <GrAdd />
            </NavLink>
           </div>
          </div>

        
    </div>
    <Footer />
    </>
  )
}

export default Tutorials