import React from 'react'
import styles from './SavedTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'
import { useNavigate, useParams } from 'react-router-dom';


const SavedTask = ({id}) => {
  
   
    const [task, setTask] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get(`notes/task${id}/`)
        .then(res => {
            setTask(res.data);
            setLoading(false);
        })
        .catch(err => {
            console.error('Error fetching task:', err);
            setLoading(false);
        });
    }, [id])
  

  if (loading) return <p>Loading...</p>

  if (!task) return <p>Task not found</p>
  
 

  
  
  
  
  
return (
   <>
    
   <div className={styles.save_cont}>
    <Header />
    
            <h1 className={styles.saved_header}>Saved TimeTable</h1>
            <div className={styles.saved_task}>
                <div className={styles.task}>
                    <p><strong>{task.id}</strong></p>
                    <p><strong>Content:</strong></p>
                    <pre>{task.list}</pre>

                </div>

            </div>
         
           

        </div>
  
    <Footer />
    </>
  )
}

export default SavedTask