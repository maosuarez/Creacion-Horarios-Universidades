"use client"

import { useState, useRef, useEffect, useId } from "react"
import { Input } from "@/components/ui/input"
import { Loader, AlertCircle } from "lucide-react"
import { getApiUrl } from "@/lib/api-client"

interface SubjectSearchProps {
  onSelectSubject: (subject: string) => void
  disabled?: boolean
}

export function SubjectSearch({ onSelectSubject, disabled }: SubjectSearchProps) {
  const [searchTerm, setSearchTerm]   = useState("")
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState("")
  const debounceTimerRef              = useRef<number | null>(null)
  const containerRef                  = useRef<HTMLDivElement>(null)
  const inputId                       = useId()
  const listboxId                     = useId()
  const errorId                       = useId()

  // Debounce de búsqueda
  useEffect(() => {
    if (!searchTerm.trim()) {
      setSuggestions([])
      setError("")
      setLoading(false)
      return
    }

    setLoading(true)
    setError("")

    if (debounceTimerRef.current !== null) {
      clearTimeout(debounceTimerRef.current)
    }

    debounceTimerRef.current = window.setTimeout(async () => {
      try {
        const response = await fetch(
          getApiUrl(`/courses/search/subjects?query=${encodeURIComponent(searchTerm)}`),
          { headers: { Authorization: `Bearer ${localStorage.getItem("authToken")}` } }
        )

        if (!response.ok) throw new Error("Error fetching subjects")

        const data = await response.json()
        const subjectList: string[] = Array.isArray(data)
          ? data.map(item => item.subject)
          : []

        setSuggestions(subjectList)

        if (subjectList.length === 0) {
          setError("No se encontraron materias con ese nombre.")
        }
      } catch {
        setError("Error al buscar materias. Intenta de nuevo.")
        setSuggestions([])
      } finally {
        setLoading(false)
      }
    }, 250)

    return () => {
      if (debounceTimerRef.current !== null) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [searchTerm])

  // Cerrar dropdown al clic fuera
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setSuggestions([])
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleSelectSubject = (subject: string) => {
    setSearchTerm("")
    setSuggestions([])
    setError("")
    onSelectSubject(subject)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setSuggestions([])
      setSearchTerm("")
    }
    if (e.key === "ArrowDown" && suggestions.length > 0) {
      e.preventDefault()
      // Foco al primer elemento del listbox
      const firstBtn = containerRef.current?.querySelector<HTMLButtonElement>('[role="option"]')
      firstBtn?.focus()
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Input
          id={inputId}
          type="text"
          placeholder="Escribe el nombre de la materia…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-label="Buscar materia"
          aria-autocomplete="list"
          aria-controls={suggestions.length > 0 ? listboxId : undefined}
          aria-expanded={suggestions.length > 0}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className="pr-9"
        />
        {loading && (
          <Loader
            size={15}
            className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-muted-foreground"
            aria-label="Buscando…"
          />
        )}
      </div>

      {/* Error inline */}
      {error && (
        <div
          id={errorId}
          role="alert"
          className="flex items-center gap-2 mt-1.5 px-3 py-2 bg-destructive/8 border border-destructive/30 rounded-md text-destructive text-xs"
        >
          <AlertCircle size={13} aria-hidden="true" className="shrink-0" />
          {error}
        </div>
      )}

      {/* Sugerencias */}
      {suggestions.length > 0 && (
        <div
          id={listboxId}
          role="listbox"
          aria-label="Materias sugeridas"
          className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-md shadow-md z-50 max-h-48 overflow-y-auto"
        >
          {suggestions.map((subject, index) => (
            <button
              key={index}
              type="button"
              role="option"
              aria-selected="false"
              onClick={() => handleSelectSubject(subject)}
              onKeyDown={(e) => {
                if (e.key === "Escape") {
                  setSuggestions([])
                  setSearchTerm("")
                }
              }}
              className="
                w-full text-left px-3 py-2 text-sm text-foreground font-medium
                hover:bg-muted transition-colors
                border-b border-border last:border-0
                focus-visible:outline-none focus-visible:bg-muted
              "
            >
              {subject}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
