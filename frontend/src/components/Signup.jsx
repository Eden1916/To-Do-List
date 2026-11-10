import {useNavigate} from 'react-router-dom'
import {useState, useEffect} from 'react'
import {authSignup} from '../api/auth'
import { Eye, EyeOff, Mail, User, Lock } from 'lucide-react'
export default function Signup() {
    const navigate = useNavigate()
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState("")
    const [comfirmPassword, setComfirmPassword] = useState("")
    const [showComfirm, setShowComfirm] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    function validEmail(){
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    }
    function validUsername(){
        return /^[a-zA-Z\s]+$/.test(value)
    }
    async function handleClick(e){
        e.preventDefault()
        setError("")
        if(username.trim() === ""||username.length < 3){setError("please enter username with character greter that 2."); return}
        if(!validUsername(username)){setError("Only characters ans space are allowed."); return}
        if(!validEmail(email)){setError("Please enter valid email."); return}
        if(email.trim() === "" || email.length === 0){setError("please enter your email."); return}
        if(password.length < 6){setError("Password length must be at least 6"); return}
        if(password !== comfirmPassword) {setError("password and comfirm password should match"); return}
        setLoading(true)

        try{
            const user = await auth({username, email, password})
            if(user){navigate("/Dashboard")}
        }
        catch(err){
            setError("Sign up Failed")
        }
        finally{
            setLoading(false)
        }
    }
    return(
        <div className="min-h-screen bg-gray-800 flex flex-col items-center justify-center " onSubmit={handleClick}>
                    <form className="space-y-5 bg-gray-600 rounded-lg p-5 m-15">
                     <h2 className="font-bold text-2xl text-center">Sign up</h2>
                      {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex items-start gap-2">
                          <span className="mt-0.5">⚠</span>
                          <span>{error}</span>
                        </div>
                      )}
                      <div>
                        <label className="block text-sm font-medium text-gray-900 mb-1.5">
                          User Name
                        </label>
                        <div className="relative">
                          <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                            <input 
                            required
                             value={username} 
                             onChange={(e) => setUsername(e.target.value)} 
                             className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-400 transition"/>
                            </div>
                            </div>
                        <div>
                        <label className="block text-sm font-medium text-gray-900 mb-1.5">
                          Email Address
                        </label>
                        <div className="relative">
                          <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                            <input 
                            required
                             type="email" 
                             value={email} 
                             onChange={(e) => setEmail(e.target.value)} 
                             className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-400 transition"/>
                            </div>
                            </div>
                        <div>
                        <label className="block text-sm font-medium text-gray-900 mb-1.5">
                          Password
                        </label>
                        <div className="relative">
                          <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                          <input
                            type={showPassword ? "text" : "password"}
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 px-5 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-400 transition"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-700 transition"
                          >
                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        </div>
                        <div>
                        <label className="block text-sm font-medium text-gray-900 mb-1.5">
                          Comfirm Password
                        </label>
                        <div className="relative">
                          <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                          <input
                            type={showComfirm ? "text" : "password"}
                            required
                            value={comfirmPassword}
                            onChange={(e) => setComfirmPassword(e.target.value)}
                            placeholder="Enter your password"
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-12 py-3 px-5 text-sm focus:outline-none focus:ring-2 focus:ring-red-950 focus:border-transparent bg-gray-400 transition"
                          />
                          <button
                            type="button"
                            onClick={() => setShowComfirm(!showComfirm)}
                            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-700 transition"
                          >
                            {showComfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        </div>
                        <button 
                        type="submit"
                        disabled={loading} 
                        className="bg-gray-900 text-white rounded p-1 w-full hover:bg-gray-800 cursor-pointer active-bg-gray-900 active-text-white">
                        {loading === true ? (
                          <span className="flex items-center justify-center gap-2">
                            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                            </svg>
                            Signing up...
                          </span>
                        ) : "Sign up"}
                        </button>
                        <div className="mt-6 pt-6 border-t border-gray-100 text-center text-sm text-gray-400">
                          Already have an account?{" "}
                           <button onClick={() => navigate("/")} className="text-gray-950 font-semibold hover:underline hover:cursor-pointer">
                              Sign in
                           </button>
                        </div>
                    </form>
                    
                </div>
    )
}