import THeader from "./THeader"
import styles from "./CreateT.module.css"
import Footer from '../ui/Footer'
import React, { useState, useRef } from "react";
import { useNavigate } from 'react-router-dom'

const CreateT = () => {
  return (
   <>
    <div className={styles.createT_con}>
       <THeader />
    </div>
    <Footer />
    </> 
  )
}

export default CreateT