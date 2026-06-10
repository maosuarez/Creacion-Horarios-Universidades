"use client"

import { useState, useRef, useEffect, useId } from "react"
import { X, ChevronDown } from "lucide-react"

interface MultiSelectProps {
  label: string
  options: (string | number)[]
  selected: (string | number)[]
  onChange: (selected: (string | number)[]) => void
}

export function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const [open, setOpen]     = useState(false)
  const [search, setSearch] = useState("")
  const containerRef        = useRef<HTMLDivElement>(null)
  const searchRef           = useRef<HTMLInputElement>(null)
  const triggerId           = useId()
  const listboxId           = useId()

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setSearch("")
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // Foco al abrir
  useEffect(() => {
    if (open) searchRef.current?.focus()
  }, [open])

  const filteredOptions = options.filter((opt) =>
    String(opt).toLowerCase().includes(search.toLowerCase())
  )

  const handleSelect = (option: string | number) => {
    const newSelected = selected.includes(option)
      ? selected.filter((s) => s !== option)
      : [...selected, option]
    onChange(newSelected)
  }

  const handleTriggerKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
      e.preventDefault()
      setOpen(true)
    }
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpen(false)
      setSearch("")
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <label
        htmlFor={triggerId}
        className="text-sm font-medium text-foreground block mb-1.5"
      >
        {label}
      </label>

      {/* Trigger */}
      <button
        id={triggerId}
        type="button"
        onClick={() => { setOpen(!open); setSearch("") }}
        onKeyDown={handleTriggerKeyDown}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listboxId}
        className={`
          w-full px-3 py-2 bg-background border rounded-md text-sm
          flex justify-between items-center gap-2 text-left
          transition-colors
          ${open
            ? "border-primary ring-1 ring-ring"
            : "border-border hover:border-primary/60"
          }
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
        `}
      >
        <span className={selected.length === 0 ? "text-muted-foreground" : "text-foreground"}>
          {selected.length === 0
            ? "Selecciona opciones…"
            : `${selected.length} ${selected.length === 1 ? "seleccionado" : "seleccionados"}`
          }
        </span>
        <ChevronDown
          size={15}
          aria-hidden="true"
          className={`shrink-0 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {/* Tags de selección */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2" role="group" aria-label={`${label} seleccionados`}>
          {selected.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 px-2 py-0.5 bg-secondary text-secondary-foreground rounded text-xs font-medium"
            >
              {item}
              <button
                type="button"
                onClick={() => handleSelect(item)}
                aria-label={`Quitar ${item}`}
                className="hover:text-destructive transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring rounded"
              >
                <X size={11} aria-hidden="true" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Dropdown */}
      {open && (
        <div
          id={listboxId}
          role="listbox"
          aria-multiselectable="true"
          aria-label={label}
          className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-md shadow-md z-50 overflow-hidden"
        >
          {/* Búsqueda */}
          <div className="px-2 pt-2 pb-1 border-b border-border">
            <input
              ref={searchRef}
              type="text"
              placeholder="Buscar…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              aria-label="Buscar opciones"
              className="
                w-full px-2 py-1.5 bg-background border border-border rounded text-sm
                text-foreground placeholder:text-muted-foreground
                focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring
              "
            />
          </div>

          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.length === 0 ? (
              <p className="px-3 py-3 text-sm text-muted-foreground text-center">
                Sin resultados
              </p>
            ) : (
              filteredOptions.map((option) => {
                const isSelected = selected.includes(option)
                return (
                  <button
                    key={option}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => handleSelect(option)}
                    className={`
                      w-full px-3 py-2 text-left text-sm transition-colors flex items-center gap-2
                      ${isSelected
                        ? "bg-secondary text-secondary-foreground font-medium"
                        : "text-foreground hover:bg-muted"
                      }
                      focus-visible:outline-none focus-visible:bg-muted
                    `}
                  >
                    {/* Indicador de selección */}
                    <span
                      className={`
                        w-4 h-4 rounded border shrink-0 flex items-center justify-center
                        ${isSelected ? "bg-primary border-primary" : "border-border"}
                      `}
                      aria-hidden="true"
                    >
                      {isSelected && (
                        <svg viewBox="0 0 10 8" className="w-2.5 h-2.5 text-primary-foreground" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="1,4 4,7 9,1" />
                        </svg>
                      )}
                    </span>
                    {option}
                  </button>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
