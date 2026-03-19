import React from 'react'
import styles from './TaskCreate.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { useNavigate, useParams } from 'react-router-dom';

const TaskCreate = () => {
  const [title, setTitle] = useState("");
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate()


  const createTask = () => {
    setLoading(true)
    if(!title.trim() || !task.trim()){
      alert("Title and content are required")
      return
    }

    api.post('notes/task/', {
      title: title,
      task: task
    })
    .then(res => {
      //setTitle("")
      //setTask("")
      console.log(res.data)
      const taskId = res.data.id
      console.log("ID:", res.data.id)
      alert("Task created succesfully")
      setLoading(false)
      navigate(`/saved_task/${taskId}`);
    })
   .catch(err => {
    console.error('Failed to create task:', err);
    if (err.response) {
        // Server responded with 4xx/5xx
        alert("Server error: " + (err.response.data.error || "Unknown error"));
        console.log("Response data:", err.response.data);
    } else if (err.request) {
        alert("No response from server might be network issue");
    } else {
        alert("Request setup error: " + err.message);
    }
    setLoading(false);
})

  }
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  return (
   <>
   <div className={styles.task_container}>
        <Header />

        <div className={styles.task_area}>
           
           <div className={styles.task_heading}>
            <h1>Timetable Builder</h1>
           </div>
           
           <div className={styles.task_title}>
             <textarea
                      type="text"
                      className={styles.create_task}
                      placeholder="Write Your Title Here..."
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                     
             ></textarea>
           </div>


           <div className={styles.task_list}>
            <textarea
                      type="text"
                      className={styles.create_list}
                      placeholder="Write Your List Here.."
                      value={task}
                      onChange={(e) => setTask(e.target.value)}
                     
             ></textarea>
           </div>


            <button className={styles.task_submit} onClick={createTask}>
               Create
           </button> 
        </div>




        
       
    </div>
    <Footer />
    </>
  )
}

export default TaskCreate




// Pol 1231, Pol 1232, Pol 1233, Pol 1234, Pol 1235, Pol 1236, Pol 1237