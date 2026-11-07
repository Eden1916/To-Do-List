import { ListTodo, CircleCheck, Clock, Pencil, Trash2, Send } from "lucide-react";
import { Card } from "./components/ui/card";
import { ModeToggle } from "./components/mode-toggle";
import { Button } from "./components/ui/button";
import {useState, useEffect} from "react"
import {useNavigate} from "react-router-dom"

export default function Dashboard() {

  const [recentTask, setRecentTask] = useState([])
  const navigate = useNavigate()
  const token = localStorage.getItem("token")

  useEffect(()=>{
    fetch(`${import.meta.env.VITE_API_URL}/tasks`,{
      headers:{
        Authentication:`Beare${token}`
      }
      }
      .then((r)=> r.json())
      .then((d)=> {
      if(d.succes){
        setRecentTask(d.tasks.slice(0,3))
      }})
    )
  })
  const cards = [
    { label: "Total Tasks", value: 10, icon: ListTodo, path:"/tasks", color: "bg-blue-400" },
    { label: "Completed Tasks", value: 5, icon: CircleCheck, path:"/tasks/completed", color: "bg-green-400" },
    { label: "Pending Tasks", value: 5, icon: Clock, path:"/tasks/pending", color: "bg-yellow-400" },
  ];

  return (
    <div className="min-h-screen space-y-6 bg-white dark:bg-gray-900 text-black dark:text-white pb-5">
      {/* Header */}
      <div className="bg-gray-400 dark:bg-blue-950 shadow-sm p-6 flex flex-row items-center justify-between gap-4">
        <h1 className="flex-1 text-3xl font-bold text-black dark:text-white">To-Do List Bot</h1>
        <ModeToggle />
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <button
              key={card.label}
              onClick={() =>navigate(card.path)}
              className="w-full bg-gray-200 dark:bg-gray-800 rounded-lg p-6 shadow-md"
            >
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${card.color}`}
              >
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {card.label}
              </h2>
              <p className="text-2xl font-bold text-black dark:text-white">
                {card.value}
              </p>
            </button>
          );
        })}
      </div>

      {/* Task list */}
      <div className="rounded bg-gray-200 dark:bg-gray-800 p-6">
        <div className="p-2">
          <h2 className="text-lg font-bold text-black dark:text-white">My Tasks</h2>
        </div>
        {recentTask.length === 0 ? (
          <p>You haven't enter any task yet</p>) :(
            <div className="space-y">
            {recentTask.map((task)=>{
              <card key={task} className="bg-gray-100 dark:bg-gray-700 p-4 flex flex-row w-full items-center justify-between gap-4 m-3">
                <div className="flex-1">
              <h2 className="text-lg font-bold text-black dark:text-white">
                {task.title}
              </h2>
              </div>
              </card>
            })}
            </div>
          )}
          </div>

      {/* Message input */}
      <div className="bg-gray-300 dark:bg-gray-800 p-5 flex flex-row justify-between items-center gap-3 rounded-lg mx-5">
        <div className="flex-1 p-3">
          <input
            className="w-full border border-gray-400 dark:border-gray-600 bg-white dark:bg-gray-700 text-black dark:text-white placeholder-gray-500 dark:placeholder-gray-400 rounded p-3"
            placeholder="Your message"
          />
        </div>
        <div className="flex">
          <Button variant="outline" size="icon" aria-label="Send">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}