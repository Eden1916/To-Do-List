import {ListTodo, CircleCheck, Clock, Pencil, Trash2, Send } from "lucide-react"
import { Card,CardHeader, CardTitle} from "./components/ui/card";
import { ModeToggle } from "./components/mode-toggle";
import {Button} from "./components/ui/button";
export default function Dashboard() {

    const cards = [
        { label: "Total Tasks", value: 10, icon: ListTodo, color: "bg-blue-400"},
        { label: "Completed Tasks", value: 5, icon: CircleCheck, color: "bg-green-400"},
        { label: "Pending Tasks", value:5, icon: Clock, color: "bg-yellow-400"},
    ]
    return (
        <div className="space-y-6">
            <div className="bg-blue-950 shadow-sm p-6 flex felx-rows items-center justify-between gap-4">
                <h1 className="flex-1 text-3xl font-bold text-white">
                    To-Do List Bot
                </h1>
                <Button variant="outline" size="icon" aria-label="Edit Task">
                <ModeToggle className="w-4 h-4"/>
                </Button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {cards.map((card)=> {
                    const Icon = card.icon;
                    return (
                    <div key={card.label} className="w-full bg-white rounded-lg p-6 shadow-md">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${card.color}`}>
                            <Icon className="w-5 h-5 text-white"/>
                            </div>
                        <h2 className="text-sm text-gray-500 mt-1">{card.label}</h2>
                        <p className="text-2xl font-bold text-gray-800">{card.value}</p>
                        </div>
                )})}
                </div>
                
                <div className="rounded bg-gray-200 p-6">
                  <div className="p-2">
                    <h2 className="text-lg font-bold text-Black">
                      My Tasks
                    </h2>
                  </div>
                  <Card className="bg-gray-300 p-4 flex flex-row w-full items-center justify-between gap-4 m-2">
                    <div className="flex-1">
                    <h2 className=" text-lg font-bold text-gray-800">Finish the project I started</h2>
                    <p className="text-gray-600">pending</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="icon" aria-label="Edit Task">
                            <Pencil className="w-4 h-4"/>
                        </Button>
                        <Button variant="outline" size="icon" aria-label="Delete Task">
                            <Trash2 className="w-4 h-4"/>
                        </Button>
                    </div>
                  </Card>
                  <Card className="bg-gray-300 p-4 flex flex-row w-full items-center justify-between gap-4 m-2">
                    <div className="flex-1">
                    <h2 className=" text-lg font-bold text-gray-800">Finish the project I started</h2>
                    <p className="text-gray-600">pending</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="icon" aria-label="Edit Task">
                            <Pencil className="w-4 h-4"/>
                        </Button>
                        <Button variant="outline" size="icon" aria-label="Delete Task">
                            <Trash2 className="w-4 h-4"/>
                        </Button>
                    </div>
                  </Card>
                </div>
                <div className="bg-gray-200 p-5 flex felx-row justify-between items-center gap-3 rounded-lg m-5">
                <div className="flex-1 p-3">
                    <input className="flex-1 w-full border-1 rounded p-3" placeholder="Your message"></input>
                    </div>
                    <div className="flex">
                        <Button variant="outline" size="icon" aria-lebel="send">
                            <Send className="w-4 h-4"/>
                        </Button>
                    </div>
                  </div>
        </div>
    )
}