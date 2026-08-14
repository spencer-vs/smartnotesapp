import THeader from "./THeader"
import styles from "./CreateT.module.css"
import Footer from '../ui/Footer'
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from 'react-router-dom'
import api from "../api/axios"
import { toast } from 'react-toastify';

const CreateT = () => {
  const [tutorial, setTutorial] = useState("");
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate();


 

  const generateLecture = async () => {
    try {
      setLoading(true);
      const res = await api.post("notes/generate_tutorials/", {
        link: tutorial
      })
      setTutorial(res.data.content);
      setLoading(false);
      navigate("/tutorials");
    } catch (error) {
        const message = error?.response?.data?.detail || "Unable to create lecture.";
        toast(message);
        setLoading(false);
    } 
      
    } 
 
  
  
  
  
  
  
  
  return (
   <>
    <div className={styles.createT_con}>
       <THeader />

       <div className={styles.create}>
        <div className={styles.card}>
        <h1 className={styles.create_header}>Create Toturials</h1>
        <input type="text"
        placeholder="Input YouTube Link"
        value={tutorial}
        className={styles.link_box}
        onChange={(e) => setTutorial(e.target.value)}
        />
        <button type="submit" onClick={generateLecture} className={styles.generate_btn} disabled={!tutorial}>
          Generate 
        </button>
        {/* {loading ? "Generating..." : "Generated"}  */}
        {loading && <div className={styles.loader}></div>}
        </div>
       </div>
    </div>
    <Footer />
    </> 
  )

 }
export default CreateT



//  {loading ? (
//           <div className={styles.loader}></div>
//         ): (
//           <button type="button" onClick={generateLecture} className={styles.generate_btn}>
//             Generate
//           </button>
//         )}