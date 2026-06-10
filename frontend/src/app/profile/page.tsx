"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useAuth } from "@/app/auth-context"
import { useRouter } from "next/navigation"
import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader, Lock, Trash2 } from "lucide-react"

export default function ProfilePage() {
  const { user, updateProfile, changePassword, deleteAccount, logout } = useAuth()
  const router = useRouter()
  const [tab, setTab] = useState<"profile" | "security" | "delete">("profile")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // Profile Form
  const [name, setName] = useState(user?.name || "")
  const [email, setEmail] = useState(user?.email || "")
  const [bio, setBio] = useState(user?.bio || "")

  // Password Form
  const [oldPassword, setOldPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  useEffect(() => {
    if (user) {
      setName(user.name)
      setEmail(user.email)
      setBio(user.bio || "")
    }
  }, [user])

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    setLoading(true)

    try {
      await updateProfile({ name, email, bio })
      setSuccess("Perfil actualizado exitosamente")
    } catch (err) {
      setError("Error al actualizar perfil")
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden")
      return
    }

    if (newPassword.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres")
      return
    }

    setLoading(true)

    try {
      await changePassword(oldPassword, newPassword)
      setSuccess("Contraseña cambiada exitosamente")
      setOldPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err) {
      setError("Error al cambiar contraseña")
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!confirm("¿Estás seguro? Esta acción no se puede deshacer.")) return

    setLoading(true)

    try {
      await deleteAccount()
      router.push("/")
    } catch (err) {
      setError("Error al eliminar cuenta")
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent mb-2">
              Perfil
            </h1>
            <p className="text-foreground/70">Administra tu información y seguridad</p>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl blur-lg"></div>
            <div className="relative bg-card border border-primary/20 rounded-2xl overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-primary/20">
                {["profile", "security", "delete"].map((t) => (
                  <button
                    key={t}
                    onClick={() => setTab(t as any)}
                    className={`flex-1 px-4 py-4 font-semibold transition-colors ${
                      tab === t
                        ? "bg-primary/10 text-primary border-b-2 border-primary"
                        : "text-foreground/60 hover:text-foreground"
                    }`}
                  >
                    {t === "profile" ? "Perfil" : t === "security" ? "Seguridad" : "Eliminar Cuenta"}
                  </button>
                ))}
              </div>

              <div className="p-6">
                {error && (
                  <div className="flex items-center gap-3 p-4 mb-6 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
                    <AlertCircle size={18} />
                    {error}
                  </div>
                )}

                {success && (
                  <div className="flex items-center gap-3 p-4 mb-6 bg-chart-4/10 border border-chart-4/30 rounded-lg text-chart-4 text-sm">
                    ✓ {success}
                  </div>
                )}

                {/* Profile Tab */}
                {tab === "profile" && (
                  <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-foreground">Nombre</label>
                      <Input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-foreground">Email</label>
                      <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-foreground">Bio (Opcional)</label>
                      <Input
                        type="text"
                        placeholder="Cuéntanos sobre ti"
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    >
                      {loading ? (
                        <>
                          <Loader size={16} className="animate-spin mr-2" />
                          Guardando...
                        </>
                      ) : (
                        "Guardar Cambios"
                      )}
                    </Button>
                  </form>
                )}

                {/* Security Tab */}
                {tab === "security" && (
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-foreground flex items-center gap-2">
                        <Lock size={16} />
                        Contraseña Actual
                      </label>
                      <Input
                        type="password"
                        placeholder="••••••••"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-foreground">Nueva Contraseña</label>
                      <Input
                        type="password"
                        placeholder="••••••••"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-foreground">Confirmar Nueva Contraseña</label>
                      <Input
                        type="password"
                        placeholder="••••••••"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="bg-background border-primary/30 mt-1"
                        required
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    >
                      {loading ? (
                        <>
                          <Loader size={16} className="animate-spin mr-2" />
                          Cambiando...
                        </>
                      ) : (
                        "Cambiar Contraseña"
                      )}
                    </Button>
                  </form>
                )}

                {/* Delete Account Tab */}
                {tab === "delete" && (
                  <div className="space-y-4">
                    <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-lg">
                      <h3 className="font-semibold text-destructive mb-2 flex items-center gap-2">
                        <Trash2 size={18} />
                        Zona de Peligro
                      </h3>
                      <p className="text-foreground/70 text-sm mb-4">
                        Eliminar tu cuenta es permanente. Todos tus datos serán eliminados.
                      </p>
                      <Button
                        onClick={handleDeleteAccount}
                        disabled={loading}
                        className="w-full bg-destructive hover:bg-destructive/90 text-destructive-foreground"
                      >
                        {loading ? (
                          <>
                            <Loader size={16} className="animate-spin mr-2" />
                            Eliminando...
                          </>
                        ) : (
                          "Eliminar Cuenta Permanentemente"
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </ProtectedRoute>
  )
}
