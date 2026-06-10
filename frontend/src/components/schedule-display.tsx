"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, FileSpreadsheet, Clock, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"

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
    // Tinte sutil que se adapta al tema (12% color + 88% superficie de card)
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

export function ScheduleDisplay({ schedules, onBack }: ScheduleDisplayProps) {
  const [currentScheduleIndex, setCurrentScheduleIndex] = useState(0)
  const [expandedCell, setExpandedCell] = useState<string | null>(null)

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
    // Paleta plana para Excel (no puede leer CSS variables)
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

  // ── Celda del grid ────────────────────────────────────────────────────────
  const renderCell = (cellContent: string, rowIdx: number, colIdx: number) => {
    const cellKey    = `${rowIdx}-${colIdx}`
    const courseInfo = getCourseInfo(cellContent)
    const isExpanded = expandedCell === cellKey
    const subjectIdx = courseInfo ? (subjectIndexMap.get(courseInfo.subject) ?? 0) : -1
    const isEmpty    = !cellContent || cellContent === ""

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
            <p className="text-xs font-semibold text-foreground leading-snug line-clamp-2">
              {cellContent}
            </p>
            {isExpanded && (
              <div className="text-xs text-muted-foreground space-y-0.5 mt-2 pt-2 border-t border-border">
                <p>Cód: {courseInfo.code}</p>
                <p className="truncate">Prof: {courseInfo.teacher_name}</p>
                {courseInfo.schedules[0]?.location && (
                  <p className="truncate">Ubic: {courseInfo.schedules[0].location}</p>
                )}
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
          {schedules.length > 1 && (
            <>
              <Button
                onClick={goToPreviousSchedule}
                variant="outline"
                size="sm"
                className="gap-1"
                aria-label="Opción anterior"
              >
                <ChevronLeft size={15} aria-hidden="true" />
                Anterior
              </Button>
              <Button
                onClick={goToNextSchedule}
                variant="outline"
                size="sm"
                className="gap-1"
                aria-label="Siguiente opción"
              >
                Siguiente
                <ChevronRight size={15} aria-hidden="true" />
              </Button>
            </>
          )}

          <Button
            onClick={exportToExcel}
            variant="outline"
            size="sm"
            className="gap-1.5"
          >
            <FileSpreadsheet size={15} aria-hidden="true" />
            Exportar Excel
          </Button>

          <Button
            onClick={onBack}
            variant="ghost"
            size="sm"
            className="gap-1.5"
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Volver
          </Button>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Presiona cualquier clase para ver código y profesor.
      </p>

      {/* ── Grid del horario ── */}
      <div className="overflow-x-auto" role="region" aria-label="Tabla de horario">
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

            {/* Filas */}
            {schedule_matrix.map((row, rowIdx) => (
              <>
                {/* Etiqueta de hora */}
                <div
                  key={`hour-${rowIdx}`}
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
              </>
            ))}
          </div>
        </div>
      </div>

      {/* ── Leyenda de materias ── */}
      {courses.length > 0 && (
        <div className="pt-4 border-t border-border space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Materias en esta opción
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
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
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
