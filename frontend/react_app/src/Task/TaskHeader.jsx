
import React, { useState, useContext } from 'react';
import styles from "./TaskHeader.module.css";
import { NavLink, useNavigate } from 'react-router-dom';
import { AuthContext } from "../context/AuthContext";



const TaskHeader = () => {
  const { auth, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  
  
  const handleLogout = () => {
    logout();
    navigate("/");
  };
  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };


  return (
    <>
   

    
    
    <div className={styles.header}>
  {/* Top bar */}
  <div className={styles.topBar}>

  <div className={styles.leftSide}>
        {auth.isAuthenticated && (
        <>
        {/* <span className={styles.username}>
          Hi, {auth.user?.username}
        </span> */}
       
          <div className={`${styles.hamburger} ${menuOpen ? styles.open : ""}`} onClick={toggleMenu} aria-label='Toggle menu'>
         <span></span>
         <span></span>
         <span></span>
      </div>
        </>
      )}
    
    </div>  
    <div className={styles.rightside}>
    <button className={styles.logout} onClick={handleLogout}>
              Logout
    </button>
    </div>
  </div>
  {/* FULLSCREEN MENU */}
  
  <div  className={`${styles.menuOverlay} ${menuOpen ? styles.open : ""}`}>
    <ul className={styles.menuLinks}>
      
      {auth.isAuthenticated ? (
                  <>
                <li className={styles.navItem}><NavLink onClick={toggleMenu} to="/" className={({ isActive }) =>
                           `${styles.navLink} ${isActive ? styles.active : ''}`
                            }>Notes</NavLink></li>
                <li className={styles.navItem}><NavLink onClick={toggleMenu} to="/lecturenotes" className={({ isActive }) =>
                           `${styles.navLink} ${isActive ? styles.active : ''}`
                            }>Lectures</NavLink></li>
              <li className={styles.navItem}><NavLink onClick={toggleMenu} to="/" className={({ isActive }) =>
                           `${styles.navLink} ${isActive ? styles.active : ''}`
                            }>Tutorials</NavLink></li>
              </>
            ) : (
                  <>
                <li className={styles.navItem}><NavLink onClick={toggleMenu} to="/login" className={({ isActive }) =>
                           `${styles.navLink} ${isActive ? styles.active : ''}`
                            }>Sign In</NavLink></li>
                <li className={styles.navItem}><NavLink onClick={toggleMenu} to="/signup" className={({ isActive }) =>
                           `${styles.navLink} ${isActive ? styles.active : ''}`
                            }>Sign Up</NavLink></li>
              
              </>
            )}
     
       
    </ul>


   
      
   
   


  </div>


    
</div>
</>
  );
};
export default TaskHeader;




