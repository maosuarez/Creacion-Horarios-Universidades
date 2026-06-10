"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/app/auth-context"
import { getApiUrl } from "@/lib/api-client"
import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { AlertCircle, Loader } from "lucide-react"

interface UserItem {
  id: number
  name: string
  email: string
  role: "creator" | "viewer"
}

export default function AdminUsersPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [users, setUsers] = useState<UserItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [actionLoading, setActionLoading] = useState<number | null>(null)

  // Redirect viewers away from this page
  useEffect(() => {
    if (user && user.role !== "creator") {
      router.push("/dashboard")
    }
  }, [user, router])

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch(getApiUrl("/auth/users"), {
        headers: { Authorization: `Bearer ${localStorage.getItem("authToken")}` },
      })
      if (!response.ok) throw new Error("Error al cargar usuarios")
      const data = await response.json()
      setUsers(data)
    } catch (err: any) {
      setError(err.message || "Error al cargar usuarios")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (user?.role === "creator") {
      fetchUsers()
    }
  }, [user, fetchUsers])

  const handleToggleRole = async (targetUser: UserItem) => {
    const newRole = targetUser.role === "viewer" ? "creator" : "viewer"
    setActionLoading(targetUser.id)
    setError("")
    try {
      const response = await fetch(getApiUrl(`/auth/users/${targetUser.id}/role`), {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({ role: newRole }),
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || "Error al cambiar rol")
      }
      await fetchUsers()
    } catch (err: any) {
      setError(err.message || "Error al cambiar rol")
    } finally {
      setActionLoading(null)
    }
  }

  const primaryAdminId = users.length > 0 ? users[0].id : null

  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-1">
              Gestión de Usuarios
            </h1>
            <p className="text-muted-foreground">Administra los roles de los usuarios registrados</p>
          </div>

          <div className="bg-card border border-border rounded-2xl overflow-hidden">
              {error && (
                <div className="flex items-center gap-3 p-4 m-4 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
                  <AlertCircle size={18} />
                  {error}
                </div>
              )}

              {loading ? (
                <div className="flex items-center justify-center py-16">
                  <Loader size={32} className="animate-spin text-primary" />
                </div>
              ) : (
                <div className="divide-y divide-primary/10">
                  {users.map((u) => {
                    const isPrimaryAdmin = u.id === primaryAdminId
                    const isCurrentUser = user?.id === String(u.id)
                    const isActioning = actionLoading === u.id

                    return (
                      <div
                        key={u.id}
                        className="flex items-center justify-between px-6 py-4 hover:bg-primary/5 transition-colors"
                      >
                        <div className="flex flex-col gap-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-semibold text-foreground truncate">{u.name}</span>
                            {isPrimaryAdmin && (
                              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/15 text-primary border border-primary/30">
                                Admin Principal
                              </span>
                            )}
                            {isCurrentUser && (
                              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/15 text-primary border border-primary/30">
                                Tú
                              </span>
                            )}
                            <span
                              className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                u.role === "creator"
                                  ? "bg-primary/10 text-primary border border-primary/25 font-semibold"
                                  : "bg-muted text-muted-foreground border border-border"
                              }`}
                            >
                              {u.role === "creator" ? "Creator" : "Viewer"}
                            </span>
                          </div>
                          <span className="text-sm text-foreground/60 truncate">{u.email}</span>
                        </div>

                        <div className="ml-4 shrink-0">
                          {!isPrimaryAdmin && !isCurrentUser && (
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={isActioning}
                              onClick={() => handleToggleRole(u)}
                              className="border-primary/30 hover:border-primary hover:bg-primary/10 hover:text-primary text-sm"
                            >
                              {isActioning ? (
                                <Loader size={14} className="animate-spin" />
                              ) : u.role === "viewer" ? (
                                "Hacer Creator"
                              ) : (
                                "Hacer Viewer"
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}

                  {users.length === 0 && !loading && (
                    <div className="text-center py-12 text-foreground/50">No hay usuarios registrados</div>
                  )}
                </div>
              )}
          </div>
        </div>
      </main>
    </ProtectedRoute>
  )
}
