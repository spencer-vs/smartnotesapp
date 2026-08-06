import React from 'react'
import Header from './Header'
import Footer from "./Footer"
import styles from "./About.module.css"
import upwork from "../assets/img/upwork_2.png"
import logo from "../assets/img/logo.png"

const About = () => {
  return (
    
    <>
    <Header />
    <div className={styles.aboutContainer}>
      <div className={styles.siteHeader}>About Site </div>
      <div className={styles.aboutSite}>
        
        <div className={styles.siteImg}>
         <img src={upwork} alt="Header"  className={styles.img__1}/>
        </div>


        <div className={styles.aboutText}>
         SmartNotes is a modern note taking site built to make note taking as easy as possible, it has features that allow creation of customised notes which are only accessible to the user, users can also log into their accounts on any device and easily access their notes, updating of already created notes, downloading and sharing of notes between devices and a seamless navigation which all together creates a great UI/UX layout that satisfy the needs of virtually all users.
        </div>
      </div>

      <div className={styles.devHeader}>About Developer </div>
      <div className={styles.aboutDev}>
        <div className={styles.siteText}>
          <img src={logo} alt="Logo"  className={styles.img__2}/>
        </div>


        <div className={styles.aboutText}>
          This site was built by Isaac Sylvester &copy; 2026. The developer is currently a 400L Political Science student of Federal University Kashere and an up and coming Web Developer from Bauchi State Nigeria. Users can contact the developer via email at isaacharu17@gmail.com or Whatsapp at 09046868547.
        </div>
      </div>
        
       
       
    </div>
     <Footer />
    </>
  )
}

export default About
