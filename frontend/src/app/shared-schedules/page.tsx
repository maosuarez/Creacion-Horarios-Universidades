"use client"

import { useEffect, useState } from "react"
import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { ScheduleDisplay } from "@/components/schedule-display"
import { Button } from "@/components/ui/button"
import { getApiUrl } from "@/lib/api-client"
import { Trash2, CalendarDays } from "lucide-react"

interface SharedScheduleItem {
  id: number
  sender_name: string
  sender_email: string
  schedule_data: any
  message: string | null
  created_at: string
}

export default function SharedSchedulesPage() {
  const [items, setItems] = useState<SharedScheduleItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [viewingSchedule, setViewingSchedule] = useState<SharedScheduleItem | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const fetchShared = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch(getApiUrl("/shared-schedules/received"), {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      })
      if (!response.ok) {
        setError("Error al cargar los horarios compartidos.")
        return
      }
      const data = await response.json()
      setItems(Array.isArray(data) ? data : [])
    } catch {
      setError("Sin conexión. Verifica tu internet e intenta de nuevo.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchShared()
  }, [])

  const handleDelete = async (id: number) => {
    setDeletingId(id)
    try {
      const response = await fetch(getApiUrl(`/shared-schedules/${id}`), {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      })
      if (response.ok) {
        setItems((prev) => prev.filter((item) => item.id !== id))
      }
    } catch {
      // Ignorar errores silenciosamente
    } finally {
      setDeletingId(null)
    }
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("es-ES", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    } catch {
      return dateStr
    }
  }

  if (viewingSchedule) {
    return (
      <ProtectedRoute>
        <Navbar />
        <main className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-sm text-muted-foreground mb-4">
            Enviado por <span className="font-medium text-foreground">{viewingSchedule.sender_name}</span>
            {viewingSchedule.message && (
              <> — &ldquo;{viewingSchedule.message}&rdquo;</>
            )}
          </p>
          <ScheduleDisplay
            schedules={[viewingSchedule.schedule_data]}
            onBack={() => setViewingSchedule(null)}
          />
        </main>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-1">Horarios compartidos</h1>
          <p className="text-muted-foreground">
            Horarios que otros usuarios te han enviado.
          </p>
        </div>

        {loading && (
          <p className="text-sm text-muted-foreground">Cargando horarios…</p>
        )}

        {error && (
          <div role="alert" className="px-4 py-3 bg-destructive/8 border border-destructive/30 rounded-lg text-destructive text-sm">
            {error}
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-3">
            <CalendarDays size={40} className="text-muted-foreground" aria-hidden="true" />
            <p className="text-muted-foreground text-sm">
              Nadie te ha compartido horarios todavía.
            </p>
          </div>
        )}

        {!loading && items.length > 0 && (
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-card border border-border rounded-xl"
              >
                <div className="space-y-0.5 min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate">
                    De: {item.sender_name}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {item.sender_email}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(item.created_at)}
                  </p>
                  {item.message && (
                    <p className="text-xs text-foreground/80 italic mt-1">
                      &ldquo;{item.message}&rdquo;
                    </p>
                  )}
                </div>

                <div className="flex gap-2 shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setViewingSchedule(item)}
                    className="hover:bg-primary/10 hover:text-primary hover:border-primary/40"
                  >
                    Ver horario
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    disabled={deletingId === item.id}
                    onClick={() => handleDelete(item.id)}
                    aria-label="Eliminar horario compartido"
                  >
                    <Trash2 size={15} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </ProtectedRoute>
  )
}
