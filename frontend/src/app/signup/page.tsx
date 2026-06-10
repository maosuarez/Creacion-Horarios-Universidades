"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useAuth } from "@/app/auth-context"
import { useRouter } from "next/navigation"
import { Navbar } from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader } from "lucide-react"
import Link from "next/link"

export default function SignupPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [role, setRole] = useState<"creator" | "viewer">("creator")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const { signup, user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (user) {
      router.push("/dashboard")
    }
  }, [user, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres")
      setLoading(false)
      return
    }

    try {
      await signup(email, password, name, role)
      router.push("/dashboard")
    } catch (err) {
      setError("Error en el registro. Intenta de nuevo.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-2xl blur-2xl"></div>
            <div className="relative bg-card border border-primary/30 rounded-2xl p-8 glow-effect space-y-6">
              <div className="text-center">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Registrarse
                </h1>
                <p className="text-foreground/60 mt-2">Crea tu cuenta para comenzar</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-3 p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Nombre</label>
                  <Input
                    type="text"
                    placeholder="Tu nombre"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={loading}
                    className="bg-background border-primary/30 focus:border-primary"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Email</label>
                  <Input
                    type="email"
                    placeholder="tu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    className="bg-background border-primary/30 focus:border-primary"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Contraseña</label>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    className="bg-background border-primary/30 focus:border-primary"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Tipo de Cuenta</label>
                  <div className="flex gap-2">
                    {(["creator", "viewer"] as const).map((r) => (
                      <button
                        key={r}
                        type="button"
                        onClick={() => setRole(r)}
                        className={`flex-1 py-2 px-3 rounded-lg border transition-all ${
                          role === r
                            ? "bg-primary border-primary text-primary-foreground"
                            : "border-primary/30 text-foreground hover:border-primary"
                        }`}
                      >
                        {r === "creator" ? "Creador" : "Estudiante"}
                      </button>
                    ))}
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90 text-foreground font-semibold"
                >
                  {loading ? (
                    <>
                      <Loader size={16} className="animate-spin mr-2" />
                      Registrando...
                    </>
                  ) : (
                    "Registrarse"
                  )}
                </Button>
              </form>

              <div className="text-center text-sm text-foreground/60">
                ¿Ya tienes cuenta?{" "}
                <Link href="/login" className="text-primary hover:text-accent transition-colors font-semibold">
                  Inicia sesión
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
