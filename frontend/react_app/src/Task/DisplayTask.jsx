import React from 'react'
import styles from './DisplayTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'
import { useNavigate, useParams } from 'react-router-dom';


const DisplayTask = () => {
   
    const [tasks, setTask] = useState([])
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    
    useEffect(() => {
        setLoading(true)
        api.get('notes/tasks/')
        .then(res => {
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
    
    <div className={styles.display_con}>
    <Header />

    <h1 className={styles.task_header}>All Task</h1>

    {tasks.length === 0 ? (
        <p className={styles.task_no}>No Task Available</p>
    ) : (
        tasks.map(task => (
            <div className={styles.task_display} key={task.id}>
             <h3 className={styles.display_title}>{task.todo_title}</h3>
             <p className={styles.display_list}>{task.todo_list}</p>

             <button onClick={() => navigate(`/saved_task${task.id}`)}>View Task</button>
            </div>
        ))
    )}
        
     
    </div>
   <Footer />
    </>
  )
}

export default DisplayTask