import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./Dashboard";
import TotalTask from "./Total";
import CompletedTasks from "./Completed"
import PendingTasks from "./Pending"
import Signup from "./components/Signup.jsx"
import Login from "./components/Login.jsx"
function App() {
  return (<>
  <Routes>
  <Route path="/" element ={<Login/>}/>
  <Route path="/Signup" element = {<Signup/>}/>
  <Route path="/Dashboard" element={<Dashboard/>}/>
  <Route path="/Tasks" element={<TotalTask/>}/>
  <Route path="/Tasks/Completed" element={<CompletedTasks/>}/>
  <Route path="/Tasks/Pending" element={<PendingTasks/>}/>
  </Routes>
    
    </>
  )
}

export default App