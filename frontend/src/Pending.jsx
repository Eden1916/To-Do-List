import {useState, useEffect} from "react"
import { ModeToggle } from "./components/mode-toggle"
export default function CompletedTasks() {
    const [pendingTasks, setPendingTasks] = useState([])
    const token = localStorage.getItem("token")
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    /*useEffect(()=>{
        fetch(`${import.meta.env.VITE_API_URL}/Tasks/Pending`,{
            headers:{Authorization:`Bearer${token}`}}
        )
        .then((r) => r.json())
        .then((d) => {
            if(d.success) {
                setTasks(d.tasks)
            }
        })
    .catch((err)=> setError("unable to load tasks"))
    .finally(()=>setLoading(false))
    })*/
    return(
        <div className="min-h-screen space-y-6 bg-white dark:bg-gray-900 text-black dark:text-white pb-5">
              {/* Header */}
              <div className="bg-gray-400 dark:bg-blue-950 shadow-sm p-6 flex flex-row items-center justify-between gap-4">
                <h1 className="flex-1 text-3xl font-bold text-black dark:text-white">To-Do List Bot</h1>
                <ModeToggle />
              </div>
              {pendingTasks.length === 0 ? (<div className="text-center text-black dark:text-white p-10">
                You have no pending task.
              </div>):(<div className="align-item-center justify-content-center">
                {pendingTasks.title}
              </div>)}
              </div>
    )
}