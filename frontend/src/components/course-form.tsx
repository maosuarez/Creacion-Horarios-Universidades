"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader } from "lucide-react"

interface Course {
  id?: string
  subject: string
  code: string
  teacher_name: string
  schedules: string[]
}

interface CourseFormProps {
  course?: Course | null
  onSave: () => void
  onCancel: () => void
}

export function CourseForm({ course, onSave, onCancel }: CourseFormProps) {
  const [formData, setFormData] = useState<Course>(
    course || {
      subject: "",
      code: "",
      teacher_name: "",
      schedules: [],
    },
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const url = course ? `/api/courses/${course.id}` : "/api/courses/"
      const method = course ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) throw new Error("Error saving course")
      onSave()
    } catch (err) {
      setError("Error al guardar curso")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mb-6 pb-6 border-b border-primary/20">
      {error && (
        <div className="flex items-center gap-3 p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive text-sm">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <div>
        <label className="text-sm font-medium text-foreground">Materia</label>
        <Input
          type="text"
          placeholder="Ej: Cálculo I"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          className="bg-background border-primary/30 mt-1"
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium text-foreground">Código</label>
        <Input
          type="text"
          placeholder="Ej: MAT101"
          value={formData.code}
          onChange={(e) => setFormData({ ...formData, code: e.target.value })}
          className="bg-background border-primary/30 mt-1"
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium text-foreground">Profesor</label>
        <Input
          type="text"
          placeholder="Ej: Dr. Juan Pérez"
          value={formData.teacher_name}
          onChange={(e) => setFormData({ ...formData, teacher_name: e.target.value })}
          className="bg-background border-primary/30 mt-1"
          required
        />
      </div>

      <div className="flex gap-2 pt-2">
        <Button
          type="submit"
          disabled={loading}
          className="flex-1 bg-gradient-to-r from-primary to-accent hover:opacity-90"
        >
          {loading ? (
            <>
              <Loader size={16} className="animate-spin mr-2" />
              Guardando...
            </>
          ) : (
            "Guardar"
          )}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} className="flex-1 bg-transparent">
          Cancelar
        </Button>
      </div>
    </form>
  )
}
