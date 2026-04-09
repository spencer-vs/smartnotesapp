import styles from "./footer.module.css"
import { NavLink, useNavigate } from 'react-router-dom';
import { AuthContext } from "../context/AuthContext";
import { useContext } from "react";
import React from "react"

const footer = () => {
  
  const { auth, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  
  
  return (
    <div>

        <div className={styles.container}>
              <div className={styles.footer}>
                <div className={styles.footerHeader}> 
                  <h1 className={styles.footerHeading}>SmartNotes</h1>
                </div>
                <div className={styles.footerRow}>
              
             
              
             
               
             <div className={styles.navList}>
             
                        <ul className={styles.footerLink}>

              {auth.isAuthenticated ? (
                 <>
                     <li className={styles.footerItem}>
                          <NavLink to="/" className={styles.footerLink_1}>
                              Home
                           </NavLink>
                      </li>


                       <li className={styles.footerItem}>
                          <NavLink to="/about" className={styles.footerLink_3}>
                             Developer
                          </NavLink>
                      </li>


                      {/* <li className={styles.footerItem}>
                          <NavLink to="/features" className={styles.footerLink_3}>
                            Features
                          </NavLink>
                      </li> */}



                      <li className={styles.footerItem}>
                          <NavLink to="/contact" className={styles.footerLink_3}>
                            Contact 
                          </NavLink>
                      </li>


                        
                 </>

              ) 
              
              : 
              
              (

              <>
                   
              
                   
                   
                   
                   
                   
                   
                   
                   <li className={styles.footerItem}>
                        <NavLink to="/" className={styles.footerLink_1}>
                            Home
                        </NavLink>
                    </li>

                     <li className={styles.footerItem}>
                          <NavLink to="/about" className={styles.footerLink_3}>
                             Developer
                          </NavLink>
                      </li>


                      <li className={styles.footerItem}>
                          <NavLink to="/login" className={styles.footerLink_4}>
                            Sign In
                          </NavLink>
                      </li>

                        <li className={styles.footerItem}>
                          <NavLink to="/signup" className={styles.footerLink_4}>
                              Sign Up
                          </NavLink>
                        </li>
              </>
              
              
              )}
                          
        
                          
        
                           

                         
                    </ul>
                  </div>

                 </div>
              </div>
           </div>
    </div>
  )
}

export default footer