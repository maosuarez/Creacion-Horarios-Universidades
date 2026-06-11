"use client"

import React, { useState } from "react"
import { ChevronLeft, ChevronRight, FileSpreadsheet, Clock, ArrowLeft, Save, Share2, List, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import { getApiUrl } from "@/lib/api-client"

interface CourseSchedule {
  day: string
  start_time: string
  end_time: string
  location?: string
}

interface CourseInfo {
  subject: string
  code: number
  teacher_name: string
  schedules: CourseSchedule[]
}

interface ScheduleResponse {
  schedule_number: number
  courses: CourseInfo[]
  schedule_matrix: string[][]
  hour_labels: string[]
  day_labels: string[]
}

interface ScheduleDisplayProps {
  schedules: ScheduleResponse[]
  onBack: () => void
  onGenerateMore?: () => void
}

/**
 * Paleta de colores para materias.
 *
 * Usa color-mix() con las variables de chart del tema → adapta automáticamente
 * a modo claro y oscuro. El texto siempre usa --foreground (máximo contraste).
 *
 * Índices 0-4 mapean a --chart-1…5, después ciclan.
 */
function subjectCellStyle(subjectIndex: number): React.CSSProperties {
  const slot = (subjectIndex % 5) + 1
  return {
    borderLeftWidth: '3px',
    borderLeftStyle: 'solid',
    borderLeftColor: `var(--chart-${slot})`,
    backgroundColor: `color-mix(in srgb, var(--chart-${slot}) 12%, var(--card))`,
  }
}

function subjectLegendStyle(subjectIndex: number): React.CSSProperties {
  const slot = (subjectIndex % 5) + 1
  return {
    borderLeftWidth: '4px',
    borderLeftStyle: 'solid',
    borderLeftColor: `var(--chart-${slot})`,
    backgroundColor: `color-mix(in srgb, var(--chart-${slot}) 8%, var(--card))`,
  }
}

function subjectBadgeStyle(subjectIndex: number): React.CSSProperties {
  const slot = (subjectIndex % 5) + 1
  return {
    backgroundColor: `color-mix(in srgb, var(--chart-${slot}) 20%, var(--card))`,
    color: `var(--chart-${slot})`,
  }
}

// Mapa de índice de columna (0-5) → nombre del día en español (como viene del backend)
const COL_TO_DAY_ES: Record<number, string> = {
  0: "Lunes",
  1: "Martes",
  2: "Miércoles",
  3: "Jueves",
  4: "Viernes",
  5: "Sábado",
}

export function ScheduleDisplay({ schedules, onBack, onGenerateMore }: ScheduleDisplayProps) {
  const [currentScheduleIndex, setCurrentScheduleIndex] = useState(0)
  const [expandedCell, setExpandedCell] = useState<string | null>(null)

  // ── Estado: guardar horario ───────────────────────────────────────────────
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [saveName, setSaveName] = useState("")
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState("")
  const [saveSuccess, setSaveSuccess] = useState(false)

  // ── Estado: compartir horario ─────────────────────────────────────────────
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [shareEmail, setShareEmail] = useState("")
  const [shareMessage, setShareMessage] = useState("")
  const [shareLoading, setShareLoading] = useState(false)
  const [shareError, setShareError] = useState("")
  const [shareSuccess, setShareSuccess] = useState(false)

  // ── Estado: drawer de materias ────────────────────────────────────────────
  const [subjectSheetOpen, setSubjectSheetOpen] = useState(false)

  if (schedules.length === 0) return null

  const currentSchedule = schedules[currentScheduleIndex]
  const { schedule_matrix, hour_labels, day_labels, courses } = currentSchedule

  const invalidShape =
    !Array.isArray(schedule_matrix) ||
    !Array.isArray(hour_labels) ||
    !Array.isArray(day_labels) ||
    !Array.isArray(courses)

  if (invalidShape) {
    return (
      <div role="alert" className="p-6 text-center text-destructive text-sm">
        Error: estructura de horario inválida. Por favor regresa e intenta de nuevo.
      </div>
    )
  }

  // Mapa: nombre de materia → índice (para color consistente)
  const subjectIndexMap = new Map<string, number>()
  courses.forEach((course, idx) => {
    subjectIndexMap.set(course.subject, idx)
  })

  const getCourseInfo = (cellContent: string): CourseInfo | null => {
    if (!cellContent) return null
    return courses.find((c) =>
      cellContent.includes(c.subject) || cellContent.includes(c.code.toString())
    ) ?? null
  }

  const goToPreviousSchedule = () => {
    setCurrentScheduleIndex((prev) => (prev === 0 ? schedules.length - 1 : prev - 1))
    setExpandedCell(null)
  }

  const goToNextSchedule = () => {
    setCurrentScheduleIndex((prev) => (prev === schedules.length - 1 ? 0 : prev + 1))
    setExpandedCell(null)
  }

  // ── Exportar a Excel ──────────────────────────────────────────────────────
  const getSubjectHexColor = (subject: string): string => {
    const EXCEL_COLORS = ['#C7D2FE', '#A7F3D0', '#FDE68A', '#BAE6FD', '#FECDD3']
    const idx = subjectIndexMap.get(subject) ?? 0
    return EXCEL_COLORS[idx % EXCEL_COLORS.length]
  }

  const exportToExcel = () => {
    let html = `
      <html xmlns:x="urn:schemas-microsoft-com:office:excel">
      <head>
        <meta charset="UTF-8">
        <style>
          table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
          th, td { border: 1px solid #CBD5E1; padding: 8px 12px; text-align: center; font-size: 12px; }
          th { background: #4F46E5; color: #fff; font-weight: 600; }
          td.hour { font-weight: 600; color: #374151; background: #F3F4F6; }
          td.empty { background: #FAFAFA; color: #9CA3AF; }
        </style>
      </head>
      <body>
        <h2 style="font-family:Arial;color:#111827;">Horario — Opción ${currentSchedule.schedule_number}</h2>
        <table>
          <thead>
            <tr>
              <th>Hora</th>
              ${day_labels.map(d => `<th>${d}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
    `

    schedule_matrix.forEach((row, rowIdx) => {
      html += "<tr>"
      html += `<td class="hour">${hour_labels[rowIdx]}</td>`
      row.forEach((cell) => {
        const course = getCourseInfo(cell)
        if (!cell || cell === "") {
          html += `<td class="empty">—</td>`
        } else {
          const bg = course ? getSubjectHexColor(course.subject) : "#EEF2FF"
          html += `<td style="background:${bg}">${cell}</td>`
        }
      })
      html += "</tr>"
    })

    html += `
          </tbody>
        </table>
        <br>
        <h3 style="font-family:Arial;color:#111827;">Detalle de cursos</h3>
        <table>
          <thead>
            <tr><th>Materia</th><th>Código</th><th>Profesor</th><th>Ubicación</th></tr>
          </thead>
          <tbody>
            ${courses.map(c => `
              <tr>
                <td>${c.subject}</td>
                <td>${c.code}</td>
                <td>${c.teacher_name}</td>
                <td>${c.schedules.map(s => s.location).filter(Boolean).join(' / ')}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </body></html>
    `

    const blob = new Blob([html], { type: "application/vnd.ms-excel" })
    const url  = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href     = url
    link.download = `Horario_Opcion_${currentSchedule.schedule_number}.xls`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // ── Guardar horario ───────────────────────────────────────────────────────
  const handleSaveSchedule = async () => {
    if (!saveName.trim()) {
      setSaveError("Escribe un nombre para el horario")
      return
    }
    setSaveLoading(true)
    setSaveError("")
    try {
      const response = await fetch(getApiUrl("/saved-schedules"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          name: saveName.trim(),
          schedule_data: currentSchedule,
        }),
      })
      if (!response.ok) {
        if (response.status === 401) setSaveError("Tu sesión ha expirado. Inicia sesión de nuevo.")
        else setSaveError("Error al guardar. Intenta de nuevo.")
        return
      }
      setSaveSuccess(true)
      setTimeout(() => {
        setSaveDialogOpen(false)
        setSaveSuccess(false)
        setSaveName("")
      }, 1200)
    } catch {
      setSaveError("Sin conexión. Verifica tu internet e intenta de nuevo.")
    } finally {
      setSaveLoading(false)
    }
  }

  // ── Compartir horario ─────────────────────────────────────────────────────
  const handleShareSchedule = async () => {
    if (!shareEmail.trim()) {
      setShareError("Ingresa el correo electrónico del destinatario")
      return
    }
    setShareLoading(true)
    setShareError("")
    try {
      const response = await fetch(getApiUrl("/shared-schedules"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          recipient_email: shareEmail.trim(),
          schedule_data: currentSchedule,
          message: shareMessage.trim() || null,
        }),
      })
      if (!response.ok) {
        if (response.status === 401) setShareError("Tu sesión ha expirado. Inicia sesión de nuevo.")
        else if (response.status === 404) setShareError("No se encontró ningún usuario con ese correo.")
        else if (response.status === 400) setShareError("No puedes compartir un horario contigo mismo.")
        else setShareError("Error al compartir. Intenta de nuevo.")
        return
      }
      setShareSuccess(true)
      setTimeout(() => {
        setShareDialogOpen(false)
        setShareSuccess(false)
        setShareEmail("")
        setShareMessage("")
      }, 1200)
    } catch {
      setShareError("Sin conexión. Verifica tu internet e intenta de nuevo.")
    } finally {
      setShareLoading(false)
    }
  }

  // ── Celda del grid ────────────────────────────────────────────────────────
  const renderCell = (cellContent: string, rowIdx: number, colIdx: number) => {
    const cellKey    = `${rowIdx}-${colIdx}`
    const courseInfo = getCourseInfo(cellContent)
    const isExpanded = expandedCell === cellKey
    const subjectIdx = courseInfo ? (subjectIndexMap.get(courseInfo.subject) ?? 0) : -1
    const isEmpty    = !cellContent || cellContent === ""

    // Buscar la ubicación del schedule que coincide con este día y hora
    let locationForCell: string | undefined
    if (courseInfo) {
      const dayNameEs = COL_TO_DAY_ES[colIdx]
      const hourLabel = hour_labels[rowIdx] // e.g. "7:00"
      const hourPrefix = hourLabel?.split(":")[0] // e.g. "7"
      const matchingSchedule = courseInfo.schedules.find((s) => {
        if (s.day !== dayNameEs) return false
        // start_time viene como "07:00" o "7:00" — comparar solo la hora
        const startHour = s.start_time?.split(":")[0]?.replace(/^0/, "")
        return startHour === hourPrefix
      })
      locationForCell = matchingSchedule?.location ?? courseInfo.schedules[0]?.location
    }

    return (
      <div
        key={cellKey}
        onClick={() => !isEmpty && setExpandedCell(isExpanded ? null : cellKey)}
        role={isEmpty ? undefined : "button"}
        tabIndex={isEmpty ? undefined : 0}
        onKeyDown={(e) => {
          if (!isEmpty && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault()
            setExpandedCell(isExpanded ? null : cellKey)
          }
        }}
        aria-expanded={isEmpty ? undefined : isExpanded}
        aria-label={courseInfo ? `${courseInfo.subject}, código ${courseInfo.code}` : undefined}
        className={`
          h-full p-2 rounded-md transition-colors
          ${isEmpty
            ? "bg-muted/40"
            : "cursor-pointer hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          }
          ${isExpanded ? "ring-2 ring-primary" : ""}
        `}
        style={courseInfo ? subjectCellStyle(subjectIdx) : undefined}
      >
        {courseInfo && (
          <div className="space-y-0.5">
            {/* Nombre del curso — siempre visible */}
            <p className="text-xs font-semibold text-foreground leading-snug line-clamp-2">
              {cellContent}
            </p>

            {/* Salón/ubicación — siempre visible cuando existe, texto muy pequeño */}
            {locationForCell && (
              <p className="text-[10px] text-muted-foreground truncate leading-tight">
                {locationForCell}
              </p>
            )}

            {/* Detalles adicionales — solo cuando expanded */}
            {isExpanded && (
              <div className="text-xs text-muted-foreground space-y-0.5 mt-2 pt-2 border-t border-border">
                <p>Cód: {courseInfo.code}</p>
                <p className="truncate">Prof: {courseInfo.teacher_name}</p>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // ── Chips de resumen ──────────────────────────────────────────────────────
  const allSlots      = currentSchedule.courses.flatMap((c) => c.schedules)
  const uniqueDays    = new Set(allSlots.map((s) => s.day)).size
  const allTimes      = allSlots.flatMap((s) => [s.start_time, s.end_time])
  const earliestTime  = allTimes.length > 0 ? allTimes.reduce((a, b) => (a < b ? a : b)) : null
  const latestTime    = allTimes.length > 0 ? allTimes.reduce((a, b) => (a > b ? a : b)) : null

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-5 surface-elevated">

      {/* ── Cabecera ── */}
      <div className="flex flex-wrap justify-between items-start gap-3">
        <div className="space-y-1.5">
          <h2 className="text-lg font-semibold text-foreground">Horarios generados</h2>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Opción {currentScheduleIndex + 1} de {schedules.length}
            </span>

            {/* Chips de resumen */}
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-secondary text-secondary-foreground rounded-full"
              aria-label={`${uniqueDays} días de clase`}
            >
              {uniqueDays} {uniqueDays === 1 ? "día" : "días"}
            </span>
            {earliestTime && latestTime && (
              <span
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-secondary text-secondary-foreground rounded-full"
                aria-label={`Horario de ${earliestTime} a ${latestTime}`}
              >
                <Clock size={11} aria-hidden="true" />
                {earliestTime} – {latestTime}
              </span>
            )}
          </div>
        </div>

        {/* Controles */}
        <div className="flex flex-wrap items-center gap-2">
          {/* ← Volver — siempre primero y visible */}
          <Button
            onClick={onBack}
            size="sm"
            className="gap-1.5 bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Volver
          </Button>

          {schedules.length > 1 && (
            <>
              <Button
                onClick={goToPreviousSchedule}
                variant="outline"
                size="sm"
                className="gap-1 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
                aria-label="Opción anterior"
              >
                <ChevronLeft size={15} aria-hidden="true" />
                Anterior
              </Button>
              <Button
                onClick={goToNextSchedule}
                variant="outline"
                size="sm"
                className="gap-1 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
                aria-label="Siguiente opción"
              >
                Siguiente
                <ChevronRight size={15} aria-hidden="true" />
              </Button>
            </>
          )}

          {/* Ver materias en drawer */}
          <Button
            onClick={() => setSubjectSheetOpen(true)}
            variant="outline"
            size="sm"
            className="gap-1.5 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
            aria-label="Ver materias de este horario"
          >
            <List size={15} aria-hidden="true" />
            Ver materias
          </Button>

          {/* Guardar horario */}
          <Button
            onClick={() => { setSaveDialogOpen(true); setSaveName(""); setSaveError(""); setSaveSuccess(false) }}
            variant="outline"
            size="sm"
            className="gap-1.5 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
          >
            <Save size={15} aria-hidden="true" />
            Guardar
          </Button>

          {/* Compartir horario */}
          <Button
            onClick={() => { setShareDialogOpen(true); setShareEmail(""); setShareMessage(""); setShareError(""); setShareSuccess(false) }}
            variant="outline"
            size="sm"
            className="gap-1.5 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
          >
            <Share2 size={15} aria-hidden="true" />
            Compartir
          </Button>

          <Button
            onClick={exportToExcel}
            variant="outline"
            size="sm"
            className="gap-1.5 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
          >
            <FileSpreadsheet size={15} aria-hidden="true" />
            Exportar Excel
          </Button>

          {/* Generar más opciones */}
          {onGenerateMore && (
            <Button
              onClick={onGenerateMore}
              variant="outline"
              size="sm"
              className="gap-1.5 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
            >
              <RefreshCw size={15} aria-hidden="true" />
              Generar más
            </Button>
          )}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Presiona cualquier clase para ver código y profesor.
      </p>

      {/* ── Grid del horario ── */}
      <div className="overflow-x-auto overflow-y-visible" role="region" aria-label="Tabla de horario">
        <div className="inline-block min-w-full">
          <div
            className="grid gap-1"
            style={{
              gridTemplateColumns: `72px repeat(${day_labels.length}, minmax(110px, 1fr))`,
            }}
          >
            {/* Headers de días */}
            <div /> {/* esquina vacía */}
            {day_labels.map((day, idx) => (
              <div
                key={idx}
                className="py-1.5 px-2 bg-muted rounded-md text-center text-xs font-semibold text-foreground"
              >
                {day}
              </div>
            ))}

            {/* Filas — cada fila envuelta en React.Fragment con key para evitar warning */}
            {schedule_matrix.map((row, rowIdx) => (
              <React.Fragment key={`row-${rowIdx}`}>
                {/* Etiqueta de hora */}
                <div
                  className="py-1.5 px-2 bg-muted rounded-md text-center text-xs font-medium text-muted-foreground flex items-center justify-center"
                >
                  {hour_labels[rowIdx]}
                </div>

                {/* Celdas */}
                {row.map((cell, colIdx) => (
                  <div key={`cell-${rowIdx}-${colIdx}`} className="min-h-[64px]">
                    {renderCell(cell, rowIdx, colIdx)}
                  </div>
                ))}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* ── Dialog: Guardar horario ── */}
      <Dialog open={saveDialogOpen} onOpenChange={(open) => { setSaveDialogOpen(open); if (!open) { setSaveError(""); setSaveSuccess(false) } }}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Guardar horario</DialogTitle>
            <DialogDescription>
              Escribe un nombre para identificar este horario en tu perfil.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-1">
            <div className="space-y-1.5">
              <Label htmlFor="save-name">Nombre</Label>
              <Input
                id="save-name"
                placeholder="Ej. Horario semestre 1"
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSaveSchedule() }}
                disabled={saveLoading || saveSuccess}
              />
            </div>
            {saveError && (
              <p className="text-sm text-destructive">{saveError}</p>
            )}
            {saveSuccess && (
              <p className="text-sm text-primary">¡Horario guardado correctamente!</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSaveDialogOpen(false)} disabled={saveLoading} className="hover:bg-primary/10 hover:text-primary">
              Cancelar
            </Button>
            <Button onClick={handleSaveSchedule} disabled={saveLoading || saveSuccess} className="bg-primary hover:bg-primary/90 text-primary-foreground">
              {saveLoading ? "Guardando…" : "Guardar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Dialog: Compartir horario ── */}
      <Dialog open={shareDialogOpen} onOpenChange={(open) => { setShareDialogOpen(open); if (!open) { setShareError(""); setShareSuccess(false) } }}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Compartir horario</DialogTitle>
            <DialogDescription>
              Ingresa el correo del usuario con quien quieres compartir este horario.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-1">
            <div className="space-y-1.5">
              <Label htmlFor="share-email">Correo del destinatario</Label>
              <Input
                id="share-email"
                type="email"
                placeholder="usuario@ejemplo.com"
                value={shareEmail}
                onChange={(e) => setShareEmail(e.target.value)}
                disabled={shareLoading || shareSuccess}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="share-message">Mensaje (opcional)</Label>
              <Textarea
                id="share-message"
                placeholder="Escribe un mensaje opcional…"
                value={shareMessage}
                onChange={(e) => setShareMessage(e.target.value)}
                disabled={shareLoading || shareSuccess}
                rows={3}
              />
            </div>
            {shareError && (
              <p className="text-sm text-destructive">{shareError}</p>
            )}
            {shareSuccess && (
              <p className="text-sm text-primary">¡Horario compartido correctamente!</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShareDialogOpen(false)} disabled={shareLoading} className="hover:bg-primary/10 hover:text-primary">
              Cancelar
            </Button>
            <Button onClick={handleShareSchedule} disabled={shareLoading || shareSuccess} className="bg-primary hover:bg-primary/90 text-primary-foreground">
              {shareLoading ? "Enviando…" : "Compartir"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Sheet: Materias en esta opción ── */}
      <Sheet open={subjectSheetOpen} onOpenChange={setSubjectSheetOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Materias en esta opción</SheetTitle>
            <SheetDescription>
              Opción {currentScheduleIndex + 1} — {courses.length} {courses.length === 1 ? "materia" : "materias"}
            </SheetDescription>
          </SheetHeader>
          <div className="space-y-3 mt-2">
            {courses.map((course, idx) => (
              <div
                key={idx}
                className="px-3 py-2.5 rounded-lg border border-border space-y-0.5"
                style={subjectLegendStyle(idx)}
              >
                <p className="text-sm font-semibold text-foreground leading-snug">
                  {course.subject}
                </p>
                <p className="text-xs text-muted-foreground">
                  <span
                    className="inline-block px-1.5 py-0.5 rounded text-xs font-mono font-bold mr-1.5"
                    style={subjectBadgeStyle(idx)}
                  >
                    {course.code}
                  </span>
                  {course.teacher_name}
                </p>
                {course.schedules.map((s, si) => (
                  <p key={si} className="text-xs text-muted-foreground">
                    {s.day} {s.start_time}–{s.end_time}
                    {s.location && <span className="ml-1 text-foreground/70">· {s.location}</span>}
                  </p>
                ))}
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>

    </div>
  )
}
