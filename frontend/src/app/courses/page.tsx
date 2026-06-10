"use client"

import { useState, useEffect } from "react"
import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, Plus, Trash2, Edit2, Search, X, Calendar, Clock } from "lucide-react"
import { CommentSection } from "@/components/comment-section"
import { getApiUrl } from "@/lib/api-client"

interface Schedule {
  day: string
  start_time: string
  end_time: string
}

interface Course {
  id: number
  subject: string
  code: number
  teacher_name: string
  schedules: Schedule[]
}

const DAY_LABELS: Record<string, string> = {
  monday: "Lunes",
  tuesday: "Martes",
  wednesday: "Miércoles",
  thursday: "Jueves",
  friday: "Viernes",
  saturday: "Sábado",
  sunday: "Domingo"
}

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)

  useEffect(() => {
    fetchCourses()
  }, [])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      setError("")
      const response = await fetch(getApiUrl("/courses/"))
      if (response.ok) {
        const data = await response.json()
        setCourses(data)
      } else {
        setError("Error al cargar cursos")
      }
    } catch (err) {
      setError("Error de conexión al cargar cursos")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("¿Eliminar este curso?")) return

    try {
      const response = await fetch(getApiUrl(`/courses/${id}`), {
        method: "DELETE",
      })
      if (response.ok) {
        setCourses(courses.filter((c) => c.id !== id))
        if (selectedCourse?.id === id) setSelectedCourse(null)
      } else {
        setError("Error al eliminar curso")
      }
    } catch (err) {
      setError("Error de conexión al eliminar curso")
      console.error(err)
    }
  }

  const filteredCourses = courses.filter(
    (course) =>
      course.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      course.code.toString().includes(searchTerm) ||
      course.teacher_name.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  if (loading) {
    return (
      <ProtectedRoute>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary border-r-2 border-accent"></div>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent mb-2">
              Gestión de Cursos
            </h1>
            <p className="text-foreground/70">Crea y administra tus cursos disponibles</p>
          </div>

          {error && (
            <div className="flex items-center gap-3 p-4 mb-6 bg-destructive/10 border border-destructive/30 rounded-lg text-destructive">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Courses List */}
            <div className="lg:col-span-2">
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl blur-lg"></div>
                <div className="relative bg-card border border-primary/20 rounded-2xl p-6">
                  <div className="flex gap-3 mb-6">
                    <div className="flex-1 relative">
                      <Search size={18} className="absolute left-3 top-3 text-foreground/40" />
                      <Input
                        placeholder="Buscar por materia, código o profesor..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="bg-background border-primary/30 pl-10"
                      />
                    </div>
                    <Button
                      onClick={() => {
                        setEditingCourse(null)
                        setShowForm(true)
                      }}
                      className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    >
                      <Plus size={18} />
                      Nuevo Curso
                    </Button>
                  </div>

                  {showForm && (
                    <CourseFormComponent
                      course={editingCourse}
                      onSave={() => {
                        setShowForm(false)
                        setEditingCourse(null)
                        fetchCourses()
                      }}
                      onCancel={() => {
                        setShowForm(false)
                        setEditingCourse(null)
                      }}
                      onError={setError}
                    />
                  )}

                  {!showForm && (
                    <div className="space-y-3">
                      {filteredCourses.length === 0 ? (
                        <div className="text-center py-8 text-foreground/60">
                          {searchTerm ? "No se encontraron cursos" : "No hay cursos disponibles"}
                        </div>
                      ) : (
                        filteredCourses.map((course) => (
                          <div
                            key={course.id}
                            onClick={() => setSelectedCourse(course)}
                            className={`p-4 border rounded-lg cursor-pointer transition-all ${
                              selectedCourse?.id === course.id
                                ? "bg-primary/10 border-primary shadow-lg"
                                : "bg-background/50 border-primary/20 hover:border-primary hover:shadow-md"
                            }`}
                          >
                            <div className="flex justify-between items-start mb-3">
                              <div className="flex-1">
                                <h3 className="font-bold text-lg text-foreground">{course.subject}</h3>
                                <p className="text-sm text-foreground/60 mt-1">{course.teacher_name}</p>
                              </div>
                              <span className="bg-accent/20 text-accent px-3 py-1 rounded-full text-sm font-semibold">
                                {course.code}
                              </span>
                            </div>

                            {/* Horarios preview */}
                            <div className="mb-3 flex flex-wrap gap-1">
                              {course.schedules.slice(0, 3).map((schedule, idx) => (
                                <span
                                  key={idx}
                                  className="text-xs bg-secondary/20 text-secondary px-2 py-1 rounded"
                                >
                                  {DAY_LABELS[schedule.day]} {schedule.start_time}-{schedule.end_time}
                                </span>
                              ))}
                              {course.schedules.length > 3 && (
                                <span className="text-xs bg-secondary/20 text-secondary px-2 py-1 rounded">
                                  +{course.schedules.length - 3} más
                                </span>
                              )}
                            </div>

                            <div className="flex gap-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setEditingCourse(course)
                                  setShowForm(true)
                                }}
                                className="flex-1 px-3 py-2 bg-accent/10 text-accent hover:bg-accent/20 rounded text-sm font-medium transition-colors flex items-center justify-center gap-1"
                              >
                                <Edit2 size={14} />
                                Editar
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleDelete(course.id)
                                }}
                                className="flex-1 px-3 py-2 bg-destructive/10 text-destructive hover:bg-destructive/20 rounded text-sm font-medium transition-colors flex items-center justify-center gap-1"
                              >
                                <Trash2 size={14} />
                                Eliminar
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Course Details & Comments */}
            {selectedCourse && !showForm && (
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-secondary/10 to-accent/10 rounded-2xl blur-lg"></div>
                <div className="relative bg-card border border-primary/20 rounded-2xl p-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-bold text-foreground mb-1">{selectedCourse.subject}</h2>
                    <p className="text-sm text-foreground/60">{selectedCourse.teacher_name}</p>
                    <span className="inline-block mt-2 bg-accent/20 text-accent px-3 py-1 rounded-full text-sm font-semibold">
                      Código: {selectedCourse.code}
                    </span>
                  </div>

                  <div className="mb-6">
                    <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                      <Calendar size={16} />
                      Horarios
                    </h3>
                    <div className="space-y-2">
                      {selectedCourse.schedules.map((schedule, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 p-3 bg-secondary/10 border border-secondary/20 rounded-lg"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-sm text-foreground">
                              {DAY_LABELS[schedule.day]}
                            </p>
                            <p className="text-xs text-foreground/60 flex items-center gap-1 mt-1">
                              <Clock size={12} />
                              {schedule.start_time} - {schedule.end_time}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <CommentSection courseId={selectedCourse.id.toString()} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </ProtectedRoute>
  )
}

// Componente de formulario integrado
function CourseFormComponent({
  course,
  onSave,
  onCancel,
  onError,
}: {
  course: Course | null
  onSave: () => void
  onCancel: () => void
  onError: (error: string) => void
}) {
  const [formData, setFormData] = useState({
    subject: course?.subject || "",
    code: course?.code?.toString() || "",
    teacher_name: course?.teacher_name || "",
  })
  const [schedules, setSchedules] = useState<Schedule[]>(
    course?.schedules || [{ day: "monday", start_time: "08:00", end_time: "10:00" }]
  )
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    // Validaciones
    if (!formData.subject.trim() || formData.subject.length > 100) {
      onError("La materia debe tener entre 1 y 100 caracteres")
      return
    }
    if (!formData.code || parseInt(formData.code) <= 0) {
      onError("El código debe ser un número positivo")
      return
    }
    if (!formData.teacher_name.trim() || formData.teacher_name.length > 100) {
      onError("El nombre del profesor debe tener entre 1 y 100 caracteres")
      return
    }
    if (schedules.length === 0 || schedules.length > 10) {
      onError("Debe haber entre 1 y 10 horarios")
      return
    }

    try {
      setSaving(true)
      onError("")

      const payload = {
        subject: formData.subject.trim(),
        code: parseInt(formData.code),
        teacher_name: formData.teacher_name.trim(),
        schedules: schedules,
      }

      const url = course ? getApiUrl(`/courses/${course.id}`) : getApiUrl("/courses/")
      const method = course ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        onSave()
      } else {
        const errorData = await response.json()
        onError(errorData.detail || "Error al guardar el curso")
      }
    } catch (err) {
      onError("Error de conexión al guardar el curso")
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const addSchedule = () => {
    if (schedules.length < 10) {
      setSchedules([...schedules, { day: "monday", start_time: "08:00", end_time: "10:00" }])
    }
  }

  const removeSchedule = (index: number) => {
    if (schedules.length > 1) {
      setSchedules(schedules.filter((_, i) => i !== index))
    }
  }

  const updateSchedule = (index: number, field: keyof Schedule, value: string) => {
    const updated = [...schedules]
    updated[index] = { ...updated[index], [field]: value }
    setSchedules(updated)
  }

  return (
    <div className="space-y-6 bg-background/50 p-6 rounded-lg border border-primary/20">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-foreground">
          {course ? "Editar Curso" : "Nuevo Curso"}
        </h3>
        <button onClick={onCancel} className="text-foreground/60 hover:text-foreground">
          <X size={20} />
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="subject">Materia *</Label>
          <Input
            id="subject"
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            placeholder="Ej: Cálculo I"
            maxLength={100}
            className="bg-background"
          />
        </div>

        <div>
          <Label htmlFor="code">Código *</Label>
          <Input
            id="code"
            type="number"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            placeholder="Ej: 1001"
            min="1"
            className="bg-background"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="teacher">Profesor *</Label>
        <Input
          id="teacher"
          value={formData.teacher_name}
          onChange={(e) => setFormData({ ...formData, teacher_name: e.target.value })}
          placeholder="Ej: Dr. Juan Pérez"
          maxLength={100}
          className="bg-background"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <Label>Horarios * (mínimo 1, máximo 10)</Label>
          <Button
            onClick={addSchedule}
            disabled={schedules.length >= 10}
            size="sm"
            variant="outline"
            className="gap-1"
          >
            <Plus size={14} />
            Agregar
          </Button>
        </div>

        <div className="space-y-3">
          {schedules.map((schedule, index) => (
            <div key={index} className="flex gap-2 p-3 bg-card border border-primary/10 rounded-lg">
              <div className="flex-1">
                <Label className="text-xs">Día</Label>
                <select
                  value={schedule.day}
                  onChange={(e) => updateSchedule(index, "day", e.target.value)}
                  className="w-full p-2 text-sm bg-background border border-primary/20 rounded mt-1"
                >
                  <option value="monday">Lunes</option>
                  <option value="tuesday">Martes</option>
                  <option value="wednesday">Miércoles</option>
                  <option value="thursday">Jueves</option>
                  <option value="friday">Viernes</option>
                  <option value="saturday">Sábado</option>
                </select>
              </div>

              <div className="flex-1">
                <Label className="text-xs">Hora inicio</Label>
                <Input
                  type="time"
                  value={schedule.start_time}
                  onChange={(e) => updateSchedule(index, "start_time", e.target.value)}
                  className="bg-background mt-1"
                />
              </div>

              <div className="flex-1">
                <Label className="text-xs">Hora fin</Label>
                <Input
                  type="time"
                  value={schedule.end_time}
                  onChange={(e) => updateSchedule(index, "end_time", e.target.value)}
                  className="bg-background mt-1"
                />
              </div>

              <div className="flex items-end">
                <Button
                  onClick={() => removeSchedule(index)}
                  disabled={schedules.length === 1}
                  size="sm"
                  variant="ghost"
                  className="text-destructive hover:bg-destructive/10"
                >
                  <Trash2 size={16} />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <Button onClick={handleSubmit} disabled={saving} className="flex-1 bg-gradient-to-r from-primary to-accent">
          {saving ? "Guardando..." : course ? "Actualizar" : "Crear Curso"}
        </Button>
        <Button onClick={onCancel} variant="outline" className="flex-1">
          Cancelar
        </Button>
      </div>
    </div>
  )
}