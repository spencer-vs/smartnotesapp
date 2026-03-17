import React from "react"
import { useState, useContext } from "react"
import api from "../api/axios"
import { useNavigate } from "react-router-dom"
import styles from "./SignIn.module.css"
import Header from "../ui/Header"
import { AuthContext } from "../context/AuthContext"

export const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate()
  const { login } = useContext(AuthContext);



  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const res = await api.post("auth/token/", { username, password });
      login(res.data);
      navigate("/");

    } catch {
      alert("Invalid Login Credentials!")
    }
  };

  
  
  
  
  return (
    <>
      <Header /> 
   
    <div className={styles.container}>
      
     <form className={styles.formWrapper}>
      <h2 className={styles.loginHeader}>Login</h2>
      <input className={styles.signinName} placeholder="Username" onChange={(e) => setUsername(e.target.value)}/>
      <input className={styles.signinPassword} type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)}/>
      <button className={styles.signinBTN} onClick={handleLogin}>Login</button>
     </form>

    </div>
     </>
  )
}

export default SignIn
