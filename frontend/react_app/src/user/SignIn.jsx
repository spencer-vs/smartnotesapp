import React from "react"
import { useState, useContext } from "react"
import api from "../api/axios"
import { useNavigate } from "react-router-dom"
import styles from "./SignIn.module.css"
import Header from "../ui/Header"
import { AuthContext } from "../context/AuthContext"
import { NavLink } from "react-router-dom"
import { IoMdEye } from "react-icons/io"; 
import { IoMdEyeOff } from "react-icons/io"; 
{/* <IoMdEye />
<IoMdEyeOff /> */}



export const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()
  const { login } = useContext(AuthContext);



  
 
   const togglePassword = () => {
    setShowPassword((prev) => !prev);
  }
 
  
  
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
      
     <form className={styles.formWrapper} onSubmit={handleLogin}>
      <h2 className={styles.loginHeader}>Login</h2>
      <input className={styles.signinName} placeholder="Username" onChange={(e) => setUsername(e.target.value)}/>
      <div className={styles.passwordWrapper}>
      <input className={styles.signinPassword} type={showPassword ? "text" : "password"} placeholder="Password" onChange={(e) => setPassword(e.target.value)}/>
      <button className={styles.eyecon} onClick={togglePassword} type="button">
        {showPassword  ? <IoMdEye /> : <IoMdEyeOff /> }
      </button>
      </div>
      <button className={styles.signinBTN}  type="submit">
        Login
      </button>
      {loading && (
        <div className={styles.loader}></div>
      )}

      <div>
        Don't have an account <NavLink to='/signup' className={styles.option}>Sign Up</NavLink>
      </div>

      <div>
        Forgot your password? click <NavLink to='/forgot-password' className={styles.option}>Here</NavLink>
      </div>
     </form>

    </div>
     </>
  )
}

export default SignIn


