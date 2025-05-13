import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from './Components/LandingPage';
import UploadHelper from './Components/UploadHelper';
import LogInForm from './Components/Login';
import SignUpForm from './Components/SignUp';
function App() {

  return (
    <BrowserRouter>
      <Routes>  
        <Route path='/' element = {<LandingPage/>}/>
        <Route path='/xray' element = {<UploadHelper/>}/>
        <Route path='/login' element = {<LogInForm/>}/>
        <Route path='/signup' element = {<SignUpForm/>}/>
        {/* <Route path='/upload' element = {<UploadHelper/>}/> */}
      </Routes>
    </BrowserRouter>
  )
}

export default App
