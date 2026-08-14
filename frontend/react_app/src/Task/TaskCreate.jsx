import React from 'react'
import styles from './TaskCreate.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { useNavigate, useParams } from 'react-router-dom';
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"
import TaskHeader from './TaskHeader'
import { toast } from 'react-toastify';

const TaskCreate = () => {
  const [title, setTitle] = useState("");
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate()
  const backgrounds = [bg1, bg2, bg3, bg4]
  const [index, setIndex] = useState(0)


   useEffect(() => {
    const interval = setInterval(() => {
    setIndex((prev) => (prev + 1) % backgrounds.length);
    }, 4000);
    return () => clearInterval(interval);
    }, []);


  const createTask = () => {
    setLoading(true)
    if(!title.trim() || !task.trim()){
      toast("Title and content are required")
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
      toast("Task created succesfully")
      setLoading(false)
      navigate('/display_task/');
    })
    .catch(error => {
            const message = error?.response?.data?.detail || "Unable to create task.";
            toast(message);
            setLoading(false);
        }); 

  }
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  return (
   <>
   <div className={styles.task_container}>
        <TaskHeader />

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