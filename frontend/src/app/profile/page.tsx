"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useAuth } from "@/app/auth-context"
import { useRouter } from "next/navigation"
import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader, Lock, Trash2, MessageSquare, ChevronLeft, ChevronRight } from "lucide-react"
import { getApiUrl } from "@/lib/api-client"

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

  // My Comments
  interface MyComment {
    id: number
    content: string
    course_id: number
    created_at: string
  }
  interface MyCommentsResponse {
    total: number
    page: number
    page_size: number
    comments: MyComment[]
  }
  const [myComments, setMyComments] = useState<MyCommentsResponse | null>(null)
  const [myCommentsPage, setMyCommentsPage] = useState(1)
  const [myCommentsLoading, setMyCommentsLoading] = useState(false)
  const [myCommentsError, setMyCommentsError] = useState("")
  const myCommentsPageSize = 10

  useEffect(() => {
    if (user) {
      setName(user.name)
      setEmail(user.email)
      setBio(user.bio || "")
    }
  }, [user])

  const fetchMyComments = async (page: number) => {
    try {
      setMyCommentsLoading(true)
      setMyCommentsError("")
      const token = localStorage.getItem("authToken")
      if (!token) return

      const response = await fetch(
        getApiUrl(`/comments/me/all?page=${page}&page_size=${myCommentsPageSize}`),
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      if (response.ok) {
        const data: MyCommentsResponse = await response.json()
        setMyComments(data)
      } else {
        setMyCommentsError("Error al cargar tus comentarios")
      }
    } catch (err) {
      setMyCommentsError("Error de conexión al cargar comentarios")
      console.error("Failed to fetch my comments:", err)
    } finally {
      setMyCommentsLoading(false)
    }
  }

  useEffect(() => {
    fetchMyComments(myCommentsPage)
  }, [myCommentsPage])

  const handleDeleteMyComment = async (commentId: number) => {
    if (!confirm("¿Eliminar este comentario?")) return

    try {
      const token = localStorage.getItem("authToken")
      if (!token) return

      const response = await fetch(getApiUrl(`/comments/${commentId}`), {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        await fetchMyComments(myCommentsPage)
      } else {
        setMyCommentsError("Error al eliminar el comentario")
      }
    } catch (err) {
      setMyCommentsError("Error de conexión al eliminar comentario")
      console.error("Failed to delete comment:", err)
    }
  }

  const handleDeleteAllMyComments = async () => {
    if (!confirm("¿Eliminar todos tus comentarios? Esta acción no se puede deshacer.")) return

    try {
      const token = localStorage.getItem("authToken")
      if (!token) return

      const response = await fetch(getApiUrl("/comments/me/all"), {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        setMyCommentsPage(1)
        await fetchMyComments(1)
      } else {
        setMyCommentsError("Error al eliminar los comentarios")
      }
    } catch (err) {
      setMyCommentsError("Error de conexión al eliminar comentarios")
      console.error("Failed to delete all comments:", err)
    }
  }

  const myCommentsTotalPages = myComments ? Math.ceil(myComments.total / myCommentsPageSize) : 0

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
    setError("")
    setLoading(true)
    try {
      await deleteAccount()
      router.push("/")
    } catch (err: any) {
      setError(err.message || "Error al eliminar cuenta")
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-1">
              Perfil
            </h1>
            <p className="text-muted-foreground">Administra tu información y seguridad</p>
          </div>

          <div className="bg-card border border-border rounded-2xl overflow-hidden">
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
                      className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
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
                      className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
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

          {/* My Comments Section */}
          <div className="mt-8">
            <div className="bg-card border border-border rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                  <MessageSquare size={20} />
                  Mis comentarios
                </h2>
                <div className="flex items-center gap-3">
                  {myComments && (
                    <span className="text-sm text-foreground/60">
                      {myComments.total} {myComments.total === 1 ? "comentario" : "comentarios"}
                    </span>
                  )}
                  <Button
                    onClick={handleDeleteAllMyComments}
                    size="sm"
                    variant="outline"
                    className="text-destructive border-destructive/30 hover:bg-destructive/10 hover:text-destructive text-xs"
                  >
                    Borrar todos mis comentarios
                  </Button>
                </div>
              </div>

              {myCommentsError && (
                <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
                  {myCommentsError}
                </div>
              )}

              {myCommentsLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary"></div>
                </div>
              ) : !myComments || myComments.comments.length === 0 ? (
                <div className="text-center text-foreground/60 text-sm py-8 bg-background/30 rounded-lg border border-dashed border-primary/20">
                  No has hecho ningún comentario aún.
                </div>
              ) : (
                <div className="space-y-3">
                  {myComments.comments.map((comment) => (
                    <div
                      key={comment.id}
                      className="p-4 bg-background/50 rounded-lg border border-primary/10 hover:border-primary/30 transition-colors"
                    >
                      <div className="flex justify-between items-start gap-2 mb-2">
                        <div className="flex-1">
                          <span className="font-semibold text-primary text-sm">
                            Materia #{comment.course_id}
                          </span>
                          <p className="text-foreground/40 text-xs">
                            {new Date(comment.created_at).toLocaleString("es-ES", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                        <button
                          onClick={() => handleDeleteMyComment(comment.id)}
                          className="text-destructive hover:bg-destructive/10 p-1.5 rounded transition-colors"
                          title="Eliminar comentario"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <p className="text-foreground/90 text-sm leading-relaxed whitespace-pre-wrap">
                        {comment.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {myComments && myCommentsTotalPages > 1 && (
                <div className="flex items-center justify-between pt-3 border-t border-primary/20">
                  <span className="text-xs text-foreground/60">
                    Página {myCommentsPage} de {myCommentsTotalPages}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => setMyCommentsPage((p) => Math.max(1, p - 1))}
                      disabled={myCommentsPage === 1}
                      size="sm"
                      variant="outline"
                      className="gap-1"
                    >
                      <ChevronLeft size={14} />
                      Anterior
                    </Button>
                    <Button
                      onClick={() => setMyCommentsPage((p) => Math.min(myCommentsTotalPages, p + 1))}
                      disabled={myCommentsPage === myCommentsTotalPages}
                      size="sm"
                      variant="outline"
                      className="gap-1"
                    >
                      Siguiente
                      <ChevronRight size={14} />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </ProtectedRoute>
  )
}
