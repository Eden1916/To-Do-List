export  const authLogin = async(email, password) => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/login`, {
        method:"POST",
        headers:{
            "content-type":application/json
        },
        body:JSON.stringigy(email, password)
    })
    const data = await res.json()
    if(!data.success) throw new Error(data.error || data.message || "Login Failed")

        localStorage.setItem("token", data.token)
        localStorage.setItem("user", JSON.stringify(data.user))
        return data.user;
}

export const authSignup = async(username, email, password) => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/signup`,{
        method:"POST",
        headers:{
            "content-type":application/json
        },
        body:JSON.stringify(username, email, password)

    })
    const data = await res.json()
    if(!data.success) throw new Error(data.error || data.message || "Sign up failed")

        localStorage.setItem("token", data.token)
        localStorage.setItem("user", JSON.stringify(data.user))
        return data.user
}

export const authLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
}