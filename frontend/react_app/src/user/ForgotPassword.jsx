import React from 'react'
import { useState, useContext } from "react"
import api from "../api/axios"
import { useNavigate } from "react-router-dom"
import styles from "./ForgotPassword.module.css"

const ForgotPassword = () => {
   
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            alert("Enter your email");
            return;
        }

        try {
            setLoading(true);

            await api.post("auth/forgot-password/", { email: email });

            alert("Password reset link sent to your email");
            navigate("/signin");
        } catch (err) {
            console.log(err);
            alert("Something went wrong");
        } finally {
            setLoading(false)
        }


    }

  
  
  
  
  
    return (
    <div className={styles.reset_con}>
       <form onSubmit={handleSubmit}>
        <input
           type="email"
           placeholder="Input your email"
           value={email}
           onChange={(e) => setEmail(e.target.value)}
           className={styles.input_mail}
           />

           <button className={styles.mail_btn} type="submit" disabled={loading}>
             {loading ? "Sending..." : "Send Link"}
           </button>
       </form>
    </div>
  )
}

export default ForgotPassword