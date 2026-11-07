import { useState, useEffect } from "react"
import {useNavigate} from "react-router-dom"
import {authLogin} from "../api/auth"
import { Eye, EyeOff, Mail, Lock } from "lucide-react"
export default function Login() {

    const navigate = useNavigate()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    function validEmail(value) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    }
    async function handleClick(e) {
        e.preventDefault()
        setError("")
        if(email.trim() === "" ||  !validEmail(email)){setError("invalid email!"); return}
        if(password.trim() === "") {setError("invalid password!"); return}
        if(password.length < 6) {setError("password length must be at least 6"); return}
        setLoading(true)

        try{
            const user = await authLogin({email, password}) 
            if(user){navigate("/Dashboard")}
        }
        catch(err){
            setError("Login Faild")
        }
        finally {
            setLoading(false)
        }
    }
    return(
        <div className="bg-white flex flex-column items-center justify-center " onSubmit={handleClick}>
            <form className="space-y-5 bg-gray-400 rounded-lg p-5 m-15">
             <h2 className="font-bold text-2xl text-center">Login</h2>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-start gap-2">
                  <span className="mt-0.5">⚠</span>
                  <span>{error}</span>
                </div>
              )}
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input 
                    required
                    autoComplete="email"
                     type="email" 
                     value={email} 
                     onChange={(e) => setEmail(e.target.value)} 
                     className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-50 transition"/>
                    </div>
                    </div>
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 px-5 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-50 transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                </div>
                <button 
                type="submit"
                disabled={loading} 
                className="bg-gray-600 rounded p-1 w-full hover:bg-gray-700 cursor-pointer active-bg-gray-900 active-text-white">
                {loading === true ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    Loging in...
                  </span>
                ) : "Login"}
                </button>
            </form>
        </div>
    )
}