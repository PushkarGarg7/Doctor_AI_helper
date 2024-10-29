import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {

  return (
    <BrowserRouter>
      <Routes>  
        <Route path='/' element = {<LandingPage/>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
