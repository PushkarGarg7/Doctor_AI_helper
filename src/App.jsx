import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from './Components/LandingPage';
import UploadHelper from './Components/UploadHelper';
function App() {

  return (
    <BrowserRouter>
      <Routes>  
        <Route path='/' element = {<UploadHelper/>}/>
        {/* <Route path='/upload' element = {<UploadHelper/>}/> */}
      </Routes>
    </BrowserRouter>
  )
}

export default App
