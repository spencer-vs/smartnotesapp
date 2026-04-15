import THeader from "./THeader"
import styles from "./CreateT.module.css"
import Footer from '../ui/Footer'
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from 'react-router-dom'
import api from "../api/axios"

const CreateT = () => {
  const [tutorial, setTutorial] = useState("");
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate();


  // useEffect = () => {
  //   setLoading(true)
  //   api.post("notes/generate_tutorials/")
  //   .then(res => {
  //     console.log(res.data);
  //     setTutorial(res.data);
  //     setLoading(false);
  //     navigate("/tutorials");

  //   })
  //   .catch(res => {
  //     console.log(res.error);
  //     alert("Failed to generate tutorial");
  //     setLoading(false);
  //   })
  // }

  const generateLecture = async () => {
    try {
      const res = await api.post("notes/generate_tutorials/")
      setTutorial(res.data);
      setLoading(false);
      navigate("/tutorials");
    } catch (error) {
      console.log(error);
      alert("Failed to generate tutorial");
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
        <button type="submit" onClick={generateLecture} className={styles.generate_btn}>
          Generate 
        </button>
        </div>
       </div>
    </div>
    <Footer />
    </> 
  )
}

export default CreateT