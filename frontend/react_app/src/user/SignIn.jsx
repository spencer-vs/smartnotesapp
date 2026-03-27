import React from "react"
import { useState, useContext } from "react"
import api from "../api/axios"
import { useNavigate } from "react-router-dom"
import styles from "./SignIn.module.css"
import Header from "../ui/Header"
import { AuthContext } from "../context/AuthContext"
import SIHeader from "./SIHeader"
import { NavLink } from "react-router-dom"

export const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useContext(AuthContext);



  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      setLoading(true)
      const res = await api.post("auth/token/", { username, password });
      login(res.data);
      navigate("/welcome");
      setLoading(false)

    } catch {
      alert("Invalid Login Credentials!")
      setLoading(false)
    }
  };


  

  
  
  
  
  return (
    <>
    
   
    <div className={styles.container}>
      
     <form className={styles.formWrapper}>
      <h2 className={styles.loginHeader}>Login</h2>
      <input className={styles.signinName} placeholder="Username" onChange={(e) => setUsername(e.target.value)}/>
      <input className={styles.signinPassword} type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)}/>
      <button className={styles.signinBTN} onClick={handleLogin}>
        Login
      </button>
      {loading && (
        <div className={styles.loader}></div>
      )}

      <div>
        Don't have an account <NavLink to='/signup' className={styles.option}>Sign Up</NavLink>
      </div>
     </form>

    </div>
     </>
  )
}

export default SignIn


