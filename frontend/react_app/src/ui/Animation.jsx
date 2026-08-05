import React from 'react'
import styles from "./Animation.module.css"
import logo from "../assets/img/logo.png"

import { NavLink } from "react-router-dom";


const Animations = () => {
  return (
    <div className={styles.container}>
        
       
       



    {/* <div className={styles.logo}>
      <img src={logo} alt="Logo" className={styles.logoImg} />
    </div> */}

    
     <div className={styles.scene}>
      
       <div className={styles.card}>
        <div className={`${styles.card_face} ${styles.front}`}>Welcome to SmartNotes where note taking brings joy</div>
        <div className={`${styles.card_face} ${styles.back}`}>Your all-in-one AI companion</div>
        
      </div>
     </div>



      <div className={styles.user}>
      <div className={styles.userCard}>
       
       <div className={`${styles.user_face} ${styles.user_signup}`}>
        <NavLink to="/signup" className={styles.navLink}>Sign Up</NavLink>
       </div>
       
      
      </div>
       
      
      <div className={styles.userCard2}>
       <div className={`${styles.user_face} ${styles.user_signin}`}>
         <NavLink to="/login" className={styles.navLink}>Sign In</NavLink>
       </div>
        
    
      </div>
      </div>  


    </div>
  )
}

export default Animations