import React from 'react'
import NoteHome from './Home/NoteHome'
import Header from './ui/Header'
import Footer from './ui/Footer'
import NoteCreate from './Home/NoteCreate'
import { BrowserRouter, Route } from 'react-router-dom'
import { Routes } from 'react-router-dom'
import NoteUpdate from './Home/NoteUpdate'
import SignIn from './user/SignIn'
import SignUp from "./user/SignUp"
import ProtectedRoute from './context/ProtectedRoute'
import About from './ui/About'
import Features from './ui/Features'
import Animation from './ui/Animation'
import SearchNotes from './ui/Search'
import Contact from './ui/Contact'
import TaskCreate from './Task/TaskCreate'
import SavedTask from './Task/SavedTask'
import DisplayTask from './Task/DisplayTask'
import Welcome from './ui/Welcome'
import LectureNotes from './LectureNotes/LectureNotes'
import CreateL from './LectureNotes/CreateL'
import ViewL from './LectureNotes/ViewL'
import CreateT from './Tutorial/CreateT'
import Tutorials from './Tutorial/Tutorials'
import ViewT from './Tutorial/ViewT'
import SearchLectures from './LectureNotes/SearchLecture'
import SearchTasks from './Task/SearchTasks'
import ResetPassword from './user/ResetPassword'
import ForgotPassword from './user/ForgotPassword'
import SearchT from './Tutorial/SearchT'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';





const App = () => {
  
  
  
  return (
   <>
   <ToastContainer />
   <Routes>
   
     
      <Route path="/" element={<NoteHome />}></Route>
      <Route path="/create" element={<ProtectedRoute><NoteCreate /></ProtectedRoute>}></Route>
      <Route path='/notes/:id/update' element={<ProtectedRoute><NoteUpdate /></ProtectedRoute>}></Route>
      <Route path='/login' element={<SignIn />}></Route>
      <Route path='/signup' element={<SignUp />}></Route>
      <Route path='/about' element={<About />}></Route>
      <Route path='/features' element={<Features />}></Route>
      <Route path='/animation' element={<Animation />}></Route>
      <Route path='/SearchNotes' element={<SearchNotes />}></Route>      
      <Route path='/contact' element={<Contact />}></Route> 
      <Route path='/create_task' element={<TaskCreate />}></Route> 
      <Route path='/saved_task/:id' element={<SavedTask />}></Route>
      <Route path='/display_task/' element={<DisplayTask />}></Route>
      <Route path='/welcome' element={<Welcome />}></Route>
      <Route path='/lecturenotes' element={<LectureNotes />}></Route>
      <Route path='/createlecture' element={<CreateL />}></Route>
      <Route path='/viewlecture/:id' element={<ViewL />}></Route>
      <Route path='/tutorials' element={<Tutorials />}></Route>
      <Route path='/createtutorials' element={<CreateT />}></Route>
      <Route path='/viewtutorials/:id' element={<ViewT />}></Route>
      <Route path='/searchlectures' element={<SearchLectures />}></Route>
      <Route path='/searchtasks' element={<SearchTasks />}></Route>
      <Route path='/reset-password/:uid/:token' element={<ResetPassword />}></Route>
      <Route path='/forgot-password' element={<ForgotPassword />}></Route>
       <Route path='/searchtutorial' element={<SearchT />}></Route>

  


     

   
    </Routes>
    </>
   )

  
}

export default App