"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { getApiUrl } from "@/lib/api-client"

interface User {
  id: string
  email: string
  name: string
  role: "creator" | "viewer"
  bio?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string, role: "creator" | "viewer") => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>
  deleteAccount: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("authToken")
    if (token) {
      checkAuth()
    } else {
      setIsLoading(false)
    }
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch(getApiUrl("/auth/profile"), {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      })
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem("authToken")
      }
    } catch (error) {
      console.error("Auth check failed:", error)
      localStorage.removeItem("authToken")
    } finally {
      setIsLoading(false)
    }
  }
  
  const login = async (email: string, password: string) => {
    const response = await fetch(getApiUrl("/auth/login"), {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        grant_type: "password",
        username: email,
        password: password
      }).toString()
    });
    if (!response.ok) throw new Error("Login failed");

    const data = await response.json();
    localStorage.setItem("authToken", data.access_token); // FastAPI suele devolver 'access_token'
    setUser(data.user); // Si tu backend devuelve info del usuario

    // Llamada clave: fuerza actualización real del estado global
    await checkAuth()
  };


  const signup = async (email: string, password: string, name: string, role: "creator" | "viewer") => {
    const response = await fetch(getApiUrl("/auth/signup"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name, role }),
    })
    console.log(response)
    if (!response.ok) throw new Error("Signup failed")
    const data = await response.json()
    localStorage.setItem("authToken", data.token)
    setUser(data.user)
  }

  const logout = () => {
    localStorage.removeItem("authToken")
    setUser(null)
  }

  const updateProfile = async (data: Partial<User>) => {
    const response = await fetch(getApiUrl("/auth/profile"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Update failed")
    const updated = await response.json()
    setUser(updated)
  }

  const changePassword = async (oldPassword: string, newPassword: string) => {
    const response = await fetch(getApiUrl("/auth/profile/password"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
      body: JSON.stringify({ oldPassword, newPassword }),
    })
    if (!response.ok) throw new Error("Password change failed")
  }

  const deleteAccount = async () => {
    const response = await fetch(getApiUrl("/auth/profile"), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
    })
    if (!response.ok) throw new Error("Delete failed")
    localStorage.removeItem("authToken")
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, signup, logout, updateProfile, changePassword, deleteAccount }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider")
  return context
}
