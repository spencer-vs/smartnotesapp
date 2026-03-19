import React from 'react'
import styles from './SavedTask.module.css'
import { useState, useEffect } from 'react'
import Header from '../ui/Header'
import api from "../api/axios"
import Footer from '../ui/Footer'
import { NavLink } from 'react-router-dom'
import { useNavigate, useParams } from 'react-router-dom';


const SavedTask = () => {
  
    const { id } = useParams()
    const [task, setTask] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get(`notes/task/${id}/`)
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


             <div className={styles.saved_title_1}>
                                 <textarea
                                          type="text"
                                          className={styles.saved_task}
                                          placeholder="Write Your Title Here..."
                                          value={task.todo_title}
                                          
                                         
                                 ></textarea>
                     </div>



                <div className={styles.saved_list__2}>
                                 <textarea
                                           type="text"
                                           className={styles.saved_list}
                                           placeholder="Write Your List Here.."
                                           value={task.todo_list}
                                           
                                          
                                  ></textarea>
                                </div>

            {/* <div className={styles.saved_task}>
                <div className={styles.task}>
                     <div className={styles.saved_title_1}>
                                 <textarea
                                          type="text"
                                          className={styles.saved_task}
                                          placeholder="Write Your Title Here..."
                                          value={task.todo_title}
                                          
                                         
                                 ></textarea>
                     </div>


                      <div className={styles.saved_list__2}>
                                 <textarea
                                           type="text"
                                           className={styles.saved_list}
                                           placeholder="Write Your List Here.."
                                           value={task.todo_list}
                                           
                                          
                                  ></textarea>
                                </div>
                     
                    
                     {/* <p className={styles.display_content}><strong></strong></p>
                    <p className={styles.display_content}><strong>Content:</strong></p>
                    <pre className={styles.display_content}></pre> 

                </div>

            </div>
         
            */}

        </div>
  
    <Footer />
    </>
  )
}

export default SavedTask