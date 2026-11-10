import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./Dashboard";
import TotalTask from "./TotalTasks";
import Signup from "./components/Signup.jsx"
import Login from "./components/Login.jsx"
function App() {
  return (<>
  <Routes>
  <Route path="/" element ={<Login/>}/>
  <Route path="/Signup" element = {<Signup/>}/>
  <Route path="/Dashboard" element={<Dashboard/>}/>
  </Routes>
    
    </>
  )
}

export default App