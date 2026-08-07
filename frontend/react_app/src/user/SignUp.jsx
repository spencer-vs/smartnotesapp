import React from 'react'
import { useState } from "react"
import api from "../api/axios"
import { useNavigate } from "react-router-dom"
import styles from "./SignUp.module.css"
import Header from '../ui/Header'
import { NavLink } from 'react-router-dom'
import { IoMdEye } from "react-icons/io"; 
import { IoMdEyeOff } from "react-icons/io"; 
import { toast } from 'react-toastify';
const SignUp = () => {
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("")
  const [email, setEmail] = useState("")
  const [address, setAddress] = useState("")
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()



  const togglePassword = () => {
    setShowPassword((prev) => !prev);
  }




  const validateForm = () => {
  const newErrors = {};
  if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(password)) {
    newErrors.password =
      "Password must contain letters and numbers and be at least 6 characters.";
  }
  if (!/^\d{11,}$/.test(phone)) {
    newErrors.phone = "Phone number must be at least 11 digits.";
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    newErrors.email = "Invalid email format.";
  }
  if (username.trim().length < 3) {
    newErrors.username = "Username must be at least 3 characters.";
  }
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
  
  const handleRegister = async (e) => {
  e.preventDefault();
  setLoading(true)
  if (!validateForm()) return;
  setLoading(false)
  try {
    setLoading(true)
    await api.post("auth/register/", {
      username,
      password,
      phone,
      email,
      address
    });
    toast.success("Account created successfully. Please login.");
    navigate("/login");
    setLoading(false)
  } catch (err) {
    const backendErrors = err.response?.data;
    if (backendErrors) {
      setErrors(backendErrors);
    } else {
      toast.error("Registration failed");
    }
    setLoading(false)
  } 
};
 

if (loading) return <div className={styles.loader}></div>
if (loading) return toast("Account will be created in a few seconds");


  return (
   <>
   
   <div className={styles.container}>
      
      <div className={styles.formWrapper}>
      <form onSubmit={handleRegister}>
        <h2 className={styles.registerHeader}>Create Account</h2>

        <input 
        className={styles.signupName}
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
        />
        {errors.username && <p
        className={styles.error}
        >{errors.username}</p>}

       <div className={styles.passwordBox}>
         <input 
        className={styles.signupPassword}
        type={showPassword ? "text" : "password"}
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        />
        {errors.password && <p
        className={styles.error}
        >{errors.password}</p>}

        <button className={styles.eyecons} type="button" onClick={togglePassword}>
           {showPassword ? <IoMdEye /> : <IoMdEyeOff />}
        </button>

       </div>


        <input 
        className={styles.signupPhone}
        placeholder="Phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        required
        />
        {errors.phone && <p
        className={styles.error}
        >{errors.phone}</p>}



        <input 
        className={styles.signupMail}
        type='email'
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        
        />
        {errors.email && <p
        className={styles.error}
        >{errors.email}</p>}
        

        <input 
        className={styles.signupAddress}
        type='text'
        placeholder="Address"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        
        />
        {errors.address && <p
        className={styles.error}
        >{errors.address}</p>}
      
          
      <button type="submit" className={styles.signupBTN}>
         Register
      </button>

      <div>
        Already have an account <NavLink to='/login' className={styles.option}>Sign In</NavLink>
      </div>
       {loading && (
              <div className={styles.loader}></div>
            )}
      </form>
     
      </div>
    </div>
    </>
  )
}

export default SignUp