import React from 'react'
import styles from './DisplayTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'
import { useNavigate, useParams } from 'react-router-dom';
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"

const DisplayTask = () => {
   
    const [tasks, setTask] = useState([])
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()
    const backgrounds = [bg1, bg2, bg3, bg4]
    const [index, setIndex] = useState(0)
        
        
          useEffect(() => {
            const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % backgrounds.length);
            }, 4000);
            return () => clearInterval(interval);
            }, []);
       

    const truncateWords = (text, limit) => {
    if (!text) return "";
    const words = text.split(" ");
    return words.length > limit
    ? words.slice(0, limit).join(" ") + "..."
    : text;
    };

    
    useEffect(() => {
        setLoading(true)
        api.get('notes/tasks/')
        .then(res => {
            setLoading(true)
            console.log("Task:", res.data)
            setTask(res.data)
            setLoading(false)
        })
        .catch(err => {
            console.log("Failed to fetch task:", err.message)
            setLoading(false)
        })
    }, [])
   
  
  
  
    return (
    <>
    <Header />
    <div className={styles.display_con} style={{ backgroundImage: `url(${backgrounds[index]})`}}>
    {loading && <div className={styles.loader}></div>}

   
    

    
    <h1 className={styles.task_header}>All Task</h1>

    {tasks.length === 0 ? (
        <p className={styles.task_no}>Loading Task</p>
    ) : (
        tasks.map(task => (
            <div className={styles.task_display} key={task.id}>
             <h3 className={styles.display_title}>{task.todo_title}</h3>
             <p className={styles.display_list}>{truncateWords(task.todo_list, 10)}</p>

             <button onClick={() => navigate(`/saved_task/${task.id}`)} className={styles.display_btn}>
                View Task
            </button>
            </div>
        ))
    )}
        
    
    </div>
   <Footer />
    </>
  )
}

export default DisplayTask