"use client"

import { useState, useRef, useEffect, useId } from "react"
import { Input } from "@/components/ui/input"
import { Loader } from "lucide-react"

interface AutocompleteInputProps {
  id?: string
  value: string
  onChange: (value: string) => void
  /** Recibe el texto actual y retorna las sugerencias a mostrar */
  fetchSuggestions: (query: string) => Promise<string[]>
  placeholder?: string
  maxLength?: number
  className?: string
  disabled?: boolean
}

/**
 * Input con dropdown de sugerencias obtenidas del backend.
 * Solo llama al backend cuando el valor tiene al menos 1 carácter.
 * Incluye debounce de 250 ms.
 */
export function AutocompleteInput({
  id,
  value,
  onChange,
  fetchSuggestions,
  placeholder,
  maxLength,
  className,
  disabled,
}: AutocompleteInputProps) {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading]         = useState(false)
  const [open, setOpen]               = useState(false)
  const debounceRef                   = useRef<number | null>(null)
  const containerRef                  = useRef<HTMLDivElement>(null)
  const listboxId                     = useId()

  // Fetch con debounce cada vez que cambia el valor
  useEffect(() => {
    if (debounceRef.current !== null) clearTimeout(debounceRef.current)

    if (!value.trim()) {
      setSuggestions([])
      setLoading(false)
      setOpen(false)
      return
    }

    setLoading(true)

    debounceRef.current = window.setTimeout(async () => {
      try {
        const results = await fetchSuggestions(value.trim())
        // Excluir el valor exacto ya escrito para no mostrar sugerencia redundante
        const filtered = results.filter(
          (s) => s.toLowerCase() !== value.trim().toLowerCase()
        )
        setSuggestions(filtered)
        setOpen(filtered.length > 0)
      } catch {
        setSuggestions([])
        setOpen(false)
      } finally {
        setLoading(false)
      }
    }, 250)

    return () => {
      if (debounceRef.current !== null) clearTimeout(debounceRef.current)
    }
  }, [value]) // fetchSuggestions intencionalmente omitido — es estable por diseño

  // Cerrar dropdown al clic fuera
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleSelect = (suggestion: string) => {
    onChange(suggestion)
    setSuggestions([])
    setOpen(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      setOpen(false)
    }
    if (e.key === "ArrowDown" && suggestions.length > 0) {
      e.preventDefault()
      containerRef.current?.querySelector<HTMLButtonElement>('[role="option"]')?.focus()
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Input
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => { if (suggestions.length > 0) setOpen(true) }}
          placeholder={placeholder}
          maxLength={maxLength}
          disabled={disabled}
          className={`${className ?? ""} ${loading ? "pr-9" : ""}`.trim()}
          aria-autocomplete="list"
          aria-controls={open ? listboxId : undefined}
          aria-expanded={open}
        />
        {loading && (
          <Loader
            size={15}
            className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-muted-foreground pointer-events-none"
            aria-label="Buscando…"
          />
        )}
      </div>

      {open && suggestions.length > 0 && (
        <div
          id={listboxId}
          role="listbox"
          aria-label="Sugerencias"
          className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-md shadow-md z-50 max-h-48 overflow-y-auto"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              role="option"
              aria-selected="false"
              onClick={() => handleSelect(suggestion)}
              onKeyDown={(e) => {
                if (e.key === "Escape") setOpen(false)
              }}
              className="
                w-full text-left px-3 py-2 text-sm text-foreground
                hover:bg-muted transition-colors
                border-b border-border last:border-0
                focus-visible:outline-none focus-visible:bg-muted
              "
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
