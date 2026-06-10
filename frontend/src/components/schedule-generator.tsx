"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { AlertCircle, Plus, X, Loader, Edit2, Check } from "lucide-react"
import { MultiSelect } from "@/components/multi-select"
import { SubjectSearch } from "@/components/subject-search"
import { getApiUrl } from "@/lib/api-client"
import { ScheduleDisplay } from "@/components/schedule-display"

interface CoursePreference {
  id: string
  subject: string
  teachers: string[]
  codes: string[]
  availableTeachers?: string[]
  availableCodes?: string[]
}

interface FreeTime {
  [key: string]: number[]
}

const DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
const DAY_LABELS: { [key: string]: string } = {
  monday: "Lunes",
  tuesday: "Martes",
  wednesday: "Miércoles",
  thursday: "Jueves",
  friday: "Viernes",
  saturday: "Sábado",
}

export function ScheduleGenerator() {
  const [courses, setCourses] = useState<CoursePreference[]>([])
  const [freeTime, setFreeTime] = useState<FreeTime>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [generatedSchedules, setGeneratedSchedules] = useState<any[]>([])
  const [editingCourseId, setEditingCourseId] = useState<string | null>(null)
  const [showingScheduleDisplay, setShowingScheduleDisplay] = useState(false)
  const [savedSchedulesBanner, setSavedSchedulesBanner] = useState<any[] | null>(null)

  useEffect(() => {
    if (courses.length === 0) {
      setCourses([{ id: Date.now().toString(), subject: "", teachers: [], codes: [] }])
    }
  }, [])

  useEffect(() => {
    if (!showingScheduleDisplay) {
      try {
        const saved = localStorage.getItem("lastGeneratedSchedules")
        if (saved) {
          const parsed = JSON.parse(saved)
          if (Array.isArray(parsed) && parsed.length > 0) {
            setSavedSchedulesBanner(parsed)
          }
        }
      } catch {
        localStorage.removeItem("lastGeneratedSchedules")
      }
    }
  }, [])

  useEffect(() => {
    if (generatedSchedules.length > 0) {
      try {
        localStorage.setItem("lastGeneratedSchedules", JSON.stringify(generatedSchedules))
      } catch {
        // Ignorar errores de escritura
      }
    }
  }, [generatedSchedules])

  const handleSubjectSelect = async (subject: string) => {
    const courseId = editingCourseId || `new-${Date.now()}`

    try {
      const [codesResponse, teachersResponse] = await Promise.all([
        fetch(getApiUrl(`/courses/search/codes?subject=${encodeURIComponent(subject)}`), {
          headers: { Authorization: `Bearer ${localStorage.getItem("authToken")}` },
        }),
        fetch(getApiUrl(`/courses/search/teachers?subject=${encodeURIComponent(subject)}`), {
          headers: { Authorization: `Bearer ${localStorage.getItem("authToken")}` },
        }),
      ])

      if (!codesResponse.ok || !teachersResponse.ok) {
        throw new Error("Error fetching codes or teachers")
      }

      const codesData    = await codesResponse.json()
      const teachersData = await teachersResponse.json()

      const codesList   = Array.isArray(codesData)    ? codesData.map(item => item.code)          : []
      const teachersList= Array.isArray(teachersData) ? teachersData.map(item => item.full_name)  : []

      if (codesList.length === 0 || teachersList.length === 0) {
        setError(`No se encontraron ${codesList.length === 0 ? "códigos" : "profesores"} para esta materia`)
        return
      }

      setCourses((prevCourses) => {
        const existingIndex = prevCourses.findIndex((c) => c.id === courseId)
        const newCourse: CoursePreference = {
          id: courseId,
          subject,
          teachers: [],
          codes: [],
          availableTeachers: teachersList,
          availableCodes: codesList,
        }

        if (existingIndex >= 0) {
          const updated = [...prevCourses]
          updated[existingIndex] = { ...updated[existingIndex], ...newCourse }
          return updated
        }
        return [...prevCourses, newCourse]
      })

      setEditingCourseId(null)
      setError("")
    } catch (err) {
      if (err instanceof TypeError) {
        setError("Sin conexión. Verifica tu internet e intenta de nuevo.")
      } else {
        setError("Error al cargar códigos y profesores. Intenta de nuevo.")
      }
    }
  }

  const addCourse = () => {
    setCourses([...courses, { id: Date.now().toString(), subject: "", teachers: [], codes: [] }])
  }

  const removeCourse = (id: string) => {
    setCourses(courses.filter((c) => c.id !== id))
    if (editingCourseId === id) setEditingCourseId(null)
  }

  const updateCourse = (id: string, field: string, value: any) => {
    setCourses(courses.map((c) => c.id === id ? { ...c, [field]: value } : c))
  }

  const toggleFreeTime = (day: string, hour: number) => {
    setFreeTime((prev) => {
      const dayFreeTime = prev[day] || []
      return dayFreeTime.includes(hour)
        ? { ...prev, [day]: dayFreeTime.filter((h) => h !== hour) }
        : { ...prev, [day]: [...dayFreeTime, hour].sort((a, b) => a - b) }
    })
  }

  const handleGenerateSchedule = async () => {
    setError("")
    setLoading(true)

    try {
      const payload = {
        preferencias: courses.reduce((acc, course) => {
          if (course.subject) {
            acc[course.subject] = {
              profesores: course.teachers,
              codes: course.codes.map((c) => Number.parseInt(c as string)),
            }
          }
          return acc
        }, {} as Record<string, any>),
        freetime: freeTime,
      }

      const response = await fetch(getApiUrl("/generate-schedules/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 401)      setError("Tu sesión ha expirado. Por favor inicia sesión nuevamente.")
        else if (response.status === 404) setError("No se encontraron combinaciones. Intenta con menos restricciones.")
        else if (response.status === 422) setError("Los datos enviados no son válidos. Verifica tus selecciones.")
        else if (response.status >= 500)  setError("El servidor no está disponible. Intenta más tarde.")
        else                              setError("Error al generar horarios. Intenta de nuevo.")
        setLoading(false)
        return
      }

      const data = await response.json()
      setGeneratedSchedules(Array.isArray(data) ? data : [data])
      setShowingScheduleDisplay(true)
    } catch (err) {
      setError(err instanceof TypeError
        ? "Sin conexión. Verifica tu internet e intenta de nuevo."
        : "Error al generar horarios. Intenta de nuevo."
      )
    } finally {
      setLoading(false)
    }
  }

  if (showingScheduleDisplay && generatedSchedules.length > 0) {
    return (
      <ScheduleDisplay
        schedules={generatedSchedules}
        onBack={() => {
          setShowingScheduleDisplay(false)
          setGeneratedSchedules([])
          localStorage.removeItem("lastGeneratedSchedules")
          setSavedSchedulesBanner(null)
        }}
      />
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      {/* Banner de sesión anterior */}
      {savedSchedulesBanner && (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 bg-secondary border border-border rounded-lg"
        >
          <p className="text-sm text-secondary-foreground font-medium">
            Tienes un horario guardado de tu sesión anterior
          </p>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => {
                setGeneratedSchedules(savedSchedulesBanner)
                setShowingScheduleDisplay(true)
                setSavedSchedulesBanner(null)
              }}
            >
              Ver horario
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                localStorage.removeItem("lastGeneratedSchedules")
                setSavedSchedulesBanner(null)
              }}
            >
              Descartar
            </Button>
          </div>
        </div>
      )}

      {/* Encabezado */}
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Generador de Horarios</h1>
        <p className="text-muted-foreground mt-1">
          Agrega tus materias y bloquea las horas que no quieres tener clase.
        </p>
      </div>

      {/* Error global */}
      {error && (
        <div
          role="alert"
          className="flex items-center gap-3 px-4 py-3 bg-destructive/8 border border-destructive/30 rounded-lg text-destructive text-sm"
        >
          <AlertCircle size={16} aria-hidden="true" className="shrink-0" />
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">

        {/* ── Columna izquierda: Cursos ── */}
        <section aria-labelledby="courses-heading" className="bg-card border border-border rounded-xl p-5 space-y-5 surface-elevated">
          <h2 id="courses-heading" className="text-base font-semibold text-foreground">
            Tus materias
          </h2>

          <div className="space-y-3">
            {courses.map((course) => (
              <div
                key={course.id}
                className="p-4 border border-border rounded-lg space-y-3 bg-background"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-foreground">
                    {course.subject || "Nueva materia"}
                  </span>
                  <div className="flex gap-1">
                    {course.subject && (
                      <button
                        onClick={() => editingCourseId === course.id
                          ? setEditingCourseId(null)
                          : setEditingCourseId(course.id)
                        }
                        className="p-1.5 rounded-md text-muted-foreground hover:text-primary hover:bg-muted transition-colors"
                        aria-label={editingCourseId === course.id ? "Confirmar" : `Editar ${course.subject}`}
                      >
                        {editingCourseId === course.id
                          ? <Check size={15} />
                          : <Edit2 size={15} />
                        }
                      </button>
                    )}
                    {courses.length > 1 && (
                      <button
                        onClick={() => removeCourse(course.id)}
                        className="p-1.5 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/8 transition-colors"
                        aria-label={`Eliminar ${course.subject || "materia"}`}
                      >
                        <X size={15} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Selección de materia */}
                {(editingCourseId === course.id || !course.subject) ? (
                  <SubjectSearch
                    onSelectSubject={handleSubjectSelect}
                    disabled={false}
                  />
                ) : (
                  <div className="px-3 py-2 bg-secondary rounded-md">
                    <p className="text-sm font-medium text-secondary-foreground">
                      {course.subject}
                    </p>
                  </div>
                )}

                {/* Selectores de sección y profesor */}
                {course.availableCodes && course.availableCodes.length > 0 && (
                  <MultiSelect
                    label="Secciones"
                    options={course.availableCodes.map((c) => c.toString())}
                    selected={course.codes}
                    onChange={(codes) => updateCourse(course.id, "codes", codes)}
                  />
                )}

                {course.availableTeachers && course.availableTeachers.length > 0 && (
                  <MultiSelect
                    label="Profesores preferidos"
                    options={course.availableTeachers}
                    selected={course.teachers}
                    onChange={(teachers) => updateCourse(course.id, "teachers", teachers)}
                  />
                )}
              </div>
            ))}
          </div>

          <Button
            onClick={addCourse}
            variant="outline"
            className="w-full gap-2"
          >
            <Plus size={16} aria-hidden="true" />
            Agregar materia
          </Button>

          <Button
            onClick={handleGenerateSchedule}
            disabled={loading}
            className="w-full gap-2 font-semibold"
            size="lg"
          >
            {loading
              ? <><Loader size={16} className="animate-spin" aria-hidden="true" /> Generando…</>
              : "Generar horario"
            }
          </Button>
        </section>

        {/* ── Columna derecha: Tiempo libre ── */}
        <section aria-labelledby="freetime-heading" className="bg-card border border-border rounded-xl p-5 space-y-4 surface-elevated">
          <div>
            <h2 id="freetime-heading" className="text-base font-semibold text-foreground">
              Horas que quieres libre
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Selecciona las horas donde no quieres tener ninguna clase.
            </p>
          </div>

          <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
            {DAYS_OF_WEEK.map((day) => {
              const selectedCount = (freeTime[day] || []).length
              return (
                <fieldset key={day}>
                  <legend className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                    {DAY_LABELS[day]}
                    {selectedCount > 0 && (
                      <span className="text-xs text-muted-foreground font-normal">
                        ({selectedCount} {selectedCount === 1 ? "hora" : "horas"})
                      </span>
                    )}
                  </legend>
                  <div className="grid grid-cols-4 gap-1.5">
                    {Array.from({ length: 12 }, (_, i) => i + 8).map((hour) => {
                      const isFree = freeTime[day]?.includes(hour) ?? false
                      return (
                        <button
                          key={hour}
                          onClick={() => toggleFreeTime(day, hour)}
                          aria-pressed={isFree}
                          aria-label={`${DAY_LABELS[day]} ${hour}:00${isFree ? " — libre" : ""}`}
                          className={`
                            h-9 rounded-md text-sm font-medium transition-colors
                            ${isFree
                              ? "bg-primary text-primary-foreground"
                              : "bg-background border border-border text-foreground hover:bg-muted hover:border-primary/50"
                            }
                          `}
                        >
                          {hour}h
                        </button>
                      )
                    })}
                  </div>
                </fieldset>
              )
            })}
          </div>
        </section>

      </div>
    </div>
  )
}
