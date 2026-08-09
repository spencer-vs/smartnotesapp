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
import Profile from './user/Profile';
import Pricing from './Subscription/Pricing';





const App = () => {
  
  
  
  return (
   <>
   <ToastContainer />
   <Routes>
   
     
      <Route path="/" element={<NoteHome />}></Route>
      <Route path='/login' element={<SignIn />}></Route>
      <Route path='/signup' element={<SignUp />}></Route>
      <Route path='/features' element={<Features />}></Route>
      <Route path='/animation' element={<Animation />}></Route>
      <Route path='/welcome' element={<Welcome />}></Route>
      <Route path="/create" element={<ProtectedRoute><NoteCreate /></ProtectedRoute>}></Route>
      <Route path='/notes/:id/update' element={<ProtectedRoute><NoteUpdate /></ProtectedRoute>}></Route>
      <Route path='/about' element={<ProtectedRoute><About /></ProtectedRoute>}></Route>
      <Route path='/SearchNotes' element={<ProtectedRoute><SearchNotes /></ProtectedRoute>}></Route>      
      <Route path='/contact' element={<ProtectedRoute><Contact /></ProtectedRoute>}></Route> 
      <Route path='/create_task' element={<ProtectedRoute><TaskCreate /></ProtectedRoute>}></Route> 
      <Route path='/saved_task/:id' element={<ProtectedRoute><SavedTask /></ProtectedRoute>}></Route>
      <Route path='/display_task/' element={<ProtectedRoute><DisplayTask /></ProtectedRoute>}></Route>
      <Route path='/lecturenotes' element={<ProtectedRoute><LectureNotes /></ProtectedRoute>}></Route>
      <Route path='/createlecture' element={<ProtectedRoute><CreateL /></ProtectedRoute>}></Route>
      <Route path='/viewlecture/:id' element={<ProtectedRoute><ViewL /></ProtectedRoute>}></Route>
      <Route path='/tutorials' element={<ProtectedRoute><Tutorials /></ProtectedRoute>}></Route>
      <Route path='/createtutorials' element={<ProtectedRoute><CreateT /></ProtectedRoute>}></Route>
      <Route path='/viewtutorials/:id' element={<ProtectedRoute><ViewT /></ProtectedRoute>}></Route>
      <Route path='/searchlectures' element={<ProtectedRoute><SearchLectures /></ProtectedRoute>}></Route>
      <Route path='/searchtasks' element={<ProtectedRoute><SearchTasks /></ProtectedRoute>}></Route>
      <Route path='/reset-password/:uid/:token' element={<ResetPassword />}></Route>
      <Route path='/forgot-password' element={<ForgotPassword />}></Route>
      <Route path='/searchtutorial' element={<ProtectedRoute><SearchT /></ProtectedRoute>}></Route>
      <Route path='/profile' element={<ProtectedRoute><Profile /></ProtectedRoute>}></Route>
      <Route path='/pricing' element={<ProtectedRoute><Pricing /></ProtectedRoute>}></Route>

  


     

   
    </Routes>
    </>
   )

  
}

export default App