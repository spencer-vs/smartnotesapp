
import React, { useState, useContext } from 'react';
import styles from "./SUHeader.module.css";
import { NavLink, useNavigate } from 'react-router-dom';
import { AuthContext } from "../context/AuthContext";



const SUHeader = () => {
 
 
  
  
 
 


  return (
    <>
    <div className={styles.header}>
    <div  className={styles.menu}>
    <ul className={styles.menuLinks}>
      
        <>
        
        <li className={styles.navItem}><NavLink to="/signup" >Sign Up</NavLink></li>
        </>
     
       
    </ul>


   
      
   
   


  </div>


    
</div>
</>
  );
};
export default SUHeader;




