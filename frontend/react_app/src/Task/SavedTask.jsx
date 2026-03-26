import React from 'react'
import styles from './SavedTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'
import { useNavigate, useParams } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; 
import bg1 from "../assets/img/notes_2.jpg"
import bg2 from "../assets/img/notes_1.jpg"
import bg3 from "../assets/img/notes_3.jpg"
import bg4 from "../assets/img/notes_4.jpg"
import TaskHeader from './TaskHeader'


const SavedTask = () => {
  
    const { id } = useParams()
    const [task, setTask] = useState(null)
    const [todo_title, setTitle] = useState("");
    const [todo_list, setTodo] = useState("")
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()
    const backgrounds = [bg1, bg2, bg3, bg4]
    const [index, setIndex] = useState(0)
            
            
        useEffect(() => {
        const interval = setInterval(() => {
        setIndex((prev) => (prev + 1) % backgrounds.length);
        }, 4000);
        return () => clearInterval(interval);
        }, []);

    useEffect(() => {
        api.get(`notes/task/${id}/`)
        .then(res => {
            setTask(res.data);
            setTitle(res.data.todo_title)
            setTodo(res.data.todo_list)
            setLoading(false);
        })
        .catch(err => {
            console.error('Error fetching task:', err);
            setLoading(false);
        });
    }, [id])

    const updateTask = () => {
        api.put(`notes/task/${id}/update/`, {
            'todo_title': todo_title,
            'todo_list': todo_list
        }).then(res => {
            setTask(res.data)
            setTitle(res.data.todo_title)
            setTodo(res.data.todo_list)
            alert("Task updated successfully")
            console.log(res.data);
            setLoading(false);
        })
        .catch(err => {
            console.error('Update failed:', err);
            alert("Failed to update task");
        });
  
    }


  if (loading) return <div className={styles.loader}></div>

  if (!task) return <p>Task not found</p>



  
 

  
  
  
  
  
return (
   <>
    
   <div className={styles.save_cont} style={{ backgroundImage: `url(${backgrounds[index]})`}}>
     {loading && <div className={styles.loader}></div>}
    <TaskHeader />
       
    
        <h1 className={styles.saved_header}>Update TimeTable</h1>


        <div className={styles.saved_title_1}>
            <textarea
                type="text"
                className={styles.saved_title}
                placeholder="Write Your Title Here..."
                value={todo_title || ""}
                onChange={(e) => setTitle(e.target.value)}
            ></textarea>
        </div>



        <div className={styles.saved_list__2}>
            <textarea
                type="text"
                className={styles.saved_list}
                placeholder="Write Your List Here.."
                value={todo_list || ""}
                onChange={(e) => setTodo(e.target.value)}
            ></textarea>
        </div>

        <button className={styles.updateTask} onClick={updateTask}>
            Update Task
        </button>  

        </div>
  
    <Footer />
    </>
  )
}

export default SavedTask