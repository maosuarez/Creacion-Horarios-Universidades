"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send, Trash2, Loader, MessageSquare, ChevronLeft, ChevronRight } from "lucide-react"
import { getApiUrl } from "@/lib/api-client"

interface Comment {
  id: number
  content: string
  profile_id: number
  course_id: number
  created_at: string
  author_name: string | null
  author_email: string | null
}

interface CommentListResponse {
  total: number
  page: number
  page_size: number
  comments: Comment[]
}

interface CommentSectionProps {
  courseId: string
}

export function CommentSection({ courseId }: CommentSectionProps) {
  const [commentsData, setCommentsData] = useState<CommentListResponse | null>(null)
  const [newComment, setNewComment] = useState("")
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)
  const pageSize = 10

  useEffect(() => {
    fetchComments(currentPage)
  }, [courseId, currentPage])

  useEffect(() => {
    fetchCurrentUser()
  }, [])

  const fetchCurrentUser = async () => {
    try {
      const token = localStorage.getItem("authToken")
      if (!token) return

      const response = await fetch(getApiUrl("/auth/profile"), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const profile = await response.json()
        setCurrentUserId(profile.id)
      }
    } catch (err) {
      console.error("Error fetching user profile:", err)
    }
  }

  const fetchComments = async (page: number) => {
    try {
      setLoading(true)
      setError("")
      
      const response = await fetch(
        getApiUrl(`/comments/?course_id=${courseId}&page=${page}&page_size=${pageSize}`)
      )
      
      if (response.ok) {
        const data: CommentListResponse = await response.json()
        setCommentsData(data)
      } else {
        setError("Error al cargar comentarios")
      }
    } catch (err) {
      setError("Error de conexión al cargar comentarios")
      console.error("Failed to fetch comments:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) return
    if (newComment.length > 500) {
      setError("El comentario no puede exceder 500 caracteres")
      return
    }

    try {
      setSubmitting(true)
      setError("")
      
      const token = localStorage.getItem("authToken")
      if (!token) {
        setError("Debes iniciar sesión para comentar")
        return
      }

      const response = await fetch(getApiUrl("/comments/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: newComment.trim(),
          course_id: parseInt(courseId),
        }),
      })

      if (response.ok) {
        setNewComment("")
        // Recargar primera página para ver el nuevo comentario
        setCurrentPage(1)
        await fetchComments(1)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || "Error al crear comentario")
      }
    } catch (err) {
      setError("Error de conexión al crear comentario")
      console.error("Failed to add comment:", err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm("¿Eliminar este comentario?")) return

    try {
      const token = localStorage.getItem("authToken")
      if (!token) {
        setError("Debes iniciar sesión para eliminar comentarios")
        return
      }

      const response = await fetch(getApiUrl(`/comments/${commentId}`), {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        // Recargar la página actual
        await fetchComments(currentPage)
      } else if (response.status === 403) {
        setError("No tienes permiso para eliminar este comentario")
      } else {
        setError("Error al eliminar comentario")
      }
    } catch (err) {
      setError("Error de conexión al eliminar comentario")
      console.error("Failed to delete comment:", err)
    }
  }

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && commentsData && newPage <= Math.ceil(commentsData.total / pageSize)) {
      setCurrentPage(newPage)
    }
  }

  const totalPages = commentsData ? Math.ceil(commentsData.total / pageSize) : 0
  const comments = commentsData?.comments || []

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-foreground flex items-center gap-2">
          <MessageSquare size={20} />
          Comentarios
        </h3>
        {commentsData && (
          <span className="text-sm text-foreground/60">
            {commentsData.total} {commentsData.total === 1 ? "comentario" : "comentarios"}
          </span>
        )}
      </div>

      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
          {error}
        </div>
      )}

      {/* Add Comment */}
      <div className="space-y-2">
        <Textarea
          placeholder="Escribe un comentario... (máximo 500 caracteres)"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          maxLength={500}
          className="bg-background border-primary/30 text-sm min-h-[80px] resize-none"
        />
        <div className="flex justify-between items-center">
          <span className="text-xs text-foreground/50">
            {newComment.length}/500 caracteres
          </span>
          <Button
            onClick={handleAddComment}
            disabled={submitting || !newComment.trim()}
            size="sm"
            className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
          >
            {submitting ? (
              <>
                <Loader size={14} className="animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                <Send size={14} />
                Comentar
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Comments List */}
      <div className="flex-1 overflow-y-auto space-y-3 min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary"></div>
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center text-foreground/60 text-sm py-8 bg-background/30 rounded-lg border border-dashed border-primary/20">
            No hay comentarios aún. ¡Sé el primero en comentar!
          </div>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className="p-4 bg-background/50 rounded-lg border border-primary/10 hover:border-primary/30 transition-colors"
            >
              <div className="flex justify-between items-start gap-2 mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-primary text-sm">
                      {comment.author_name || "Usuario"}
                    </span>
                    {comment.author_email && (
                      <span className="text-xs text-foreground/40">
                        ({comment.author_email})
                      </span>
                    )}
                  </div>
                  <span className="text-foreground/40 text-xs">
                    {new Date(comment.created_at).toLocaleString("es-ES", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                {currentUserId === comment.profile_id && (
                  <button
                    onClick={() => handleDeleteComment(comment.id)}
                    className="text-destructive hover:bg-destructive/10 p-1.5 rounded transition-colors"
                    title="Eliminar comentario"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
              <p className="text-foreground/90 text-sm leading-relaxed whitespace-pre-wrap">
                {comment.content}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {commentsData && totalPages > 1 && (
        <div className="flex items-center justify-between pt-3 border-t border-primary/20">
          <span className="text-xs text-foreground/60">
            Página {currentPage} de {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              size="sm"
              variant="outline"
              className="gap-1"
            >
              <ChevronLeft size={14} />
              Anterior
            </Button>
            <Button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
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
  )
}