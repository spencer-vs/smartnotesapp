import React from "react"
import styles from './Features.module.css'
import header_1 from "../assets/img/header_1.png"
import header_2 from "../assets/img/header_2.png"
import create from "../assets/img/create.png"
import footer from "../assets/img/footer.png"
import home from "../assets/img/home.png"
import login from "../assets/img/login.png"
import signup from "../assets/img/signup.png"
import update from "../assets/img/update.png"
import logo from "../assets/img/logo.png"
import contact from "../assets/img/contact.png"
import Footer from "../ui/Footer"
import { useEffect, useState } from 'react'


const Features = () => {
    const featureData = [
    {
    title: "SmartNotes",
    images: [logo],
    text: "Welcome to SmartNotes app where all your creative headaches come to an end, let's go on a journey to discover more about SmartNotes courtesy of your most kind developer."
  },
  

        {
    title: "Header Component",
    images: [header_1, header_2],
    text: "The header component is made up of two parts, the first shows a header for the logged out user, while the second shows a header for the logged in user."
  },
  {
    title: "Sign Up Component",
    images: [signup],
    text: "The Sign Up component consist of input fields for username, password, phone number and email, after succesfully filling in this information, the user will immediately be redirected to the login component where they can immediately log in and write their own customised note."
  },
  {
    title: "Login Component",
    images: [login],
    text: "The login component is one of the most exciting features of this app, it allows users to access their own customised and personalised notes given users absolute privacy."
  },
  {
    title: "Home Component",
    images: [home],
    text: "The home component is the nexus of this app, it contains all user notes with buttons that allows for deleting, updating and sharing notes across devices."
  },
  {
    title: "Create Component",
    images: [create],
    text: "The create component serves as perhaps the most important component, with a single click of the plus icon users can be able to create as much notes as they want which will be displayed at both frontend and backend."
  },
  {
    title: "Update Component",
    images: [update],
    text: "The update component allows for editing of already created notes."
  },
  {
    title: "Contact Component",
    images: [contact],
    text: "The contact component can be used by users to send a direct message to the developer via the Django admin panel."
  },
  {
    title: "Footer Component",
    images: [footer],
    text: "The footer provides important imformation about the site such as developer info and sitemap allowing for seamless navigation."
  }
];
const [current, setCurrent] = useState(0);
useEffect(() => {
  const interval = setInterval(() => {
    setCurrent((prev) => (prev + 1) % featureData.length);
  }, 9000);
  return () => clearInterval(interval);
}, []);
 
 
 
 
    return (
    <div>
      
    <div className={styles.firstFeature} >
    <div className={styles.featureInner} key={current}> 
        <h1 className={styles.firstHeader}>{featureData[current].title}</h1>
   <div className={styles.featureGrid}>
    <div className={styles.firstImage}>
      {featureData[current].images.map((img, i) => (
        <img key={i} src={img} className={styles.featureImg} />
      ))}
    </div>
    <div className={styles.firstText}>
      <p className={styles.p_1}>{featureData[current].text}</p>
    </div>
  </div>
</div>
</div>
    </div>
  )
}

export default Features