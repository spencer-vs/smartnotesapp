import React from 'react'
import NoteHome from './Home/NoteHome'
import Header from './ui/Header'
import Footer from './ui/Footer'
import NoteCreate from './Home/NoteCreate'
import { BrowserRouter, Route } from 'react-router-dom'
import { Routes } from 'react-router-dom'
import NoteUpdate from './Home/NoteUpdate'
import Carousels from './ui/Carousels'
import SignIn from './user/SignIn'
import SignUp from "./user/SignUp"
import ProtectedRoute from './context/ProtectedRoute'
import About from './ui/About'
import Features from './ui/Features'
import Animation from './ui/Animation'
import SearchNotes from './ui/Search'
import Contact from './ui/Contact'
import TaskCreate from './Task/TaskCreate'
import TaskDisplay from './Task/TaskDisplay'
import SavedTask from './Task/SavedTask'





const App = () => {
  
  
  
  return (
   <Routes>
   
     
      <Route path="/" element={<NoteHome />}></Route>
      <Route path="/create" element={<ProtectedRoute><NoteCreate /></ProtectedRoute>}></Route>
      <Route path='/notes/:id/update' element={<ProtectedRoute><NoteUpdate /></ProtectedRoute>}></Route>
      <Route path='/carousel' element={<Carousels />}></Route>
      <Route path='/login' element={<SignIn />}></Route>
      <Route path='/signup' element={<SignUp />}></Route>
      <Route path='/about' element={<About />}></Route>
      <Route path='/features' element={<Features />}></Route>
      <Route path='/animation' element={<Animation />}></Route>
      <Route path='/SearchNotes' element={<SearchNotes />}></Route>      
      <Route path='/contact' element={<Contact />}></Route> 
      <Route path='/Create_task' element={<TaskCreate />}></Route> 
      <Route path='/display_task' element={<TaskDisplay />}></Route>
      <Route path='/saved_task' element={<SavedTask />}></Route>


     

   
    </Routes>
 
   )

  
}

export default App