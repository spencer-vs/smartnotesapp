import React from 'react'
import styles from "./Welcome.module.css"
// import intro_1 from "../assets/img/intro_1.png"
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"
import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'




const Welcome = () => {
   const backgrounds = [bg1, bg2, bg3, bg4]
   const [index, setIndex] = useState(0)


   useEffect(() => {
    const interval = setInterval(() => {
    setIndex((prev) => (prev + 1) % backgrounds.length);
    }, 4000);
    return () => clearInterval(interval);
    }, []);
  
  
  
//    <div className={styles.container}>
//   <div
//     className={`${styles.bg} ${styles.active}`}
//     style={{ backgroundImage: `url(${backgrounds[index]})` }}
//   ></div>
//   <div
//     className={`${styles.bg} ${styles.next}`}
//     style={{ backgroundImage: `url(${backgrounds[(index + 1) % backgrounds.length]})` }}
//   ></div>
// </div>
//   <div className={styles.welcome}>
//           Hi Isaac, welcome back, what are we doing today.
 //style={{ backgroundImage: `url(${backgrounds[index]})`}}
//        </div>
  
    return (
    <div className={`${styles.intro_con} `}>

    

        

        
        
       
    <div className={styles.cards_row}>
    <NavLink className={styles.card1} to="/">
        <p className={styles.text_1}>Create, update, share and delete notes with ease</p>
        <button className={styles.intro_btn}>
            Notes
        </button>
    </NavLink> 

    <NavLink className={styles.card2} to="/display_task/">
        <p className={styles.text_1}>Use AI to generate timetables for your task or lectures</p>
        <button className={styles.intro_btn}>
            Task
        </button>
    </NavLink>
     
       
       
    <NavLink className={styles.card3} to="/lecturenotes">
        <p className={styles.text_1}>Record your lectures and convert them to notes using AI.</p>
        <button className={styles.intro_btn}>
            Lecture Notes
        </button>
    </NavLink> 

    <NavLink className={styles.card4} to="/tutorials">
        <p className={styles.text_1}>Turn tutorial videos into lecture notes for easy reading</p>
        <button className={styles.intro_btn}>
            Tutorials
        </button>
    </NavLink>
       
    
    </div>

    


  



    </div>
        
   
  )
}

export default Welcome