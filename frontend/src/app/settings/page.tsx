"use client"

import { useState } from 'react'
import { useSettings } from '@/app/settings-context'
import { COLOR_SCHEMES } from '@/config/color-schemes'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Palette, Type, Layout, Accessibility,
  RotateCcw, Check, Sun, Moon, Monitor,
} from 'lucide-react'
import { Navbar } from '@/components/navbar'

export default function SettingsPage() {
  const { settings, updateSettings, resetSettings } = useSettings()
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <>
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-10 space-y-10">

        {/* Encabezado */}
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-foreground">Configuración</h1>
          <p className="text-muted-foreground">
            Personaliza la apariencia para que se adapte a ti.
          </p>
        </div>

        {/* ── Modo de Tema ── */}
        <section aria-labelledby="theme-heading" className="space-y-4">
          <div className="flex items-center gap-2">
            <Sun size={18} className="text-muted-foreground" aria-hidden="true" />
            <h2 id="theme-heading" className="text-base font-semibold">Modo de Tema</h2>
          </div>

          <div className="flex gap-2 flex-wrap" role="radiogroup" aria-labelledby="theme-heading">
            {([
              { value: 'light',  label: 'Claro',   icon: <Sun size={15} /> },
              { value: 'dark',   label: 'Oscuro',  icon: <Moon size={15} /> },
              { value: 'system', label: 'Sistema', icon: <Monitor size={15} /> },
            ] as const).map(({ value, label, icon }) => (
              <button
                key={value}
                role="radio"
                aria-checked={settings.themeMode === value}
                onClick={() => updateSettings({ themeMode: value })}
                className={`
                  inline-flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium
                  border transition-colors
                  ${settings.themeMode === value
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-background text-foreground border-border hover:bg-muted'
                  }
                `}
              >
                {icon}
                {label}
              </button>
            ))}
          </div>
        </section>

        <div className="border-t border-border" />

        {/* ── Esquema de Color ── */}
        <section aria-labelledby="color-heading" className="space-y-4">
          <div className="flex items-center gap-2">
            <Palette size={18} className="text-muted-foreground" aria-hidden="true" />
            <h2 id="color-heading" className="text-base font-semibold">Color de Acento</h2>
          </div>
          <p className="text-sm text-muted-foreground -mt-2">
            Cambia el color de botones, enlaces y elementos interactivos.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3" role="radiogroup" aria-labelledby="color-heading">
            {Object.entries(COLOR_SCHEMES).map(([key, scheme]) => {
              const isSelected = settings.colorScheme === key
              return (
                <button
                  key={key}
                  role="radio"
                  aria-checked={isSelected}
                  onClick={() => updateSettings({ colorScheme: key as any })}
                  className={`
                    relative p-4 rounded-lg border-2 text-left transition-all
                    ${isSelected
                      ? 'border-primary bg-secondary'
                      : 'border-border bg-card hover:border-primary/40'
                    }
                  `}
                >
                  {/* Swatches */}
                  <div className="flex gap-1 mb-3">
                    {scheme.swatches.map((color, i) => (
                      <div
                        key={i}
                        className="h-5 flex-1 rounded-sm"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>

                  <p className="text-sm font-medium text-foreground">{scheme.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{scheme.description}</p>

                  {isSelected && (
                    <div className="absolute top-3 right-3 text-primary" aria-label="Seleccionado">
                      <Check size={14} strokeWidth={2.5} />
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </section>

        <div className="border-t border-border" />

        {/* ── Tipografía y Densidad ── */}
        <section aria-labelledby="display-heading" className="space-y-6">
          <div className="flex items-center gap-2">
            <Type size={18} className="text-muted-foreground" aria-hidden="true" />
            <h2 id="display-heading" className="text-base font-semibold">Visualización</h2>
          </div>

          {/* Tamaño de fuente */}
          <div className="space-y-2">
            <Label className="text-sm text-foreground">Tamaño de texto</Label>
            <div className="flex gap-2 flex-wrap" role="radiogroup">
              {([
                { value: 'small',  label: 'Pequeño', size: 'text-xs' },
                { value: 'medium', label: 'Mediano',  size: 'text-sm' },
                { value: 'large',  label: 'Grande',  size: 'text-base' },
              ] as const).map(({ value, label, size }) => (
                <button
                  key={value}
                  role="radio"
                  aria-checked={settings.fontSize === value}
                  onClick={() => updateSettings({ fontSize: value })}
                  className={`
                    px-4 py-2 rounded-md border transition-colors
                    ${settings.fontSize === value
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background text-foreground border-border hover:bg-muted'
                    }
                  `}
                >
                  <span className={size}>{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Densidad */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Layout size={14} className="text-muted-foreground" />
              <Label className="text-sm text-foreground">Densidad de interfaz</Label>
            </div>
            <div className="flex gap-2 flex-wrap" role="radiogroup">
              {([
                { value: 'compact',     label: 'Compacta',   hint: 'Más contenido' },
                { value: 'comfortable', label: 'Cómoda',     hint: 'Equilibrado' },
                { value: 'spacious',    label: 'Espaciosa',  hint: 'Más aire' },
              ] as const).map(({ value, label }) => (
                <button
                  key={value}
                  role="radio"
                  aria-checked={settings.density === value}
                  onClick={() => updateSettings({ density: value })}
                  className={`
                    px-4 py-2 rounded-md border text-sm transition-colors
                    ${settings.density === value
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background text-foreground border-border hover:bg-muted'
                    }
                  `}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </section>

        <div className="border-t border-border" />

        {/* ── Accesibilidad ── */}
        <section aria-labelledby="a11y-heading" className="space-y-4">
          <div className="flex items-center gap-2">
            <Accessibility size={18} className="text-muted-foreground" aria-hidden="true" />
            <h2 id="a11y-heading" className="text-base font-semibold">Accesibilidad</h2>
          </div>

          <div className="space-y-2">
            {([
              {
                key:     'showAnimations',
                label:   'Animaciones y transiciones',
                desc:    'Efectos suaves al navegar entre secciones',
                checked: settings.showAnimations,
                onChange:(v: boolean) => updateSettings({ showAnimations: v }),
              },
              {
                key:     'reducedMotion',
                label:   'Movimiento reducido',
                desc:    'Desactiva todas las animaciones (prioridad sobre lo anterior)',
                checked: settings.reducedMotion,
                onChange:(v: boolean) => updateSettings({ reducedMotion: v }),
              },
              {
                key:     'highContrast',
                label:   'Alto contraste',
                desc:    'Mejora drásticamente la visibilidad del texto y los bordes',
                checked: settings.highContrast,
                onChange:(v: boolean) => updateSettings({ highContrast: v }),
              },
            ] as const).map((item) => (
              <div
                key={item.key}
                className="flex items-center justify-between px-4 py-3 rounded-lg border border-border bg-card"
              >
                <div className="pr-4">
                  <Label htmlFor={`toggle-${item.key}`} className="text-sm font-medium cursor-pointer">
                    {item.label}
                  </Label>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.desc}</p>
                </div>
                <Switch
                  id={`toggle-${item.key}`}
                  checked={item.checked}
                  onCheckedChange={item.onChange}
                  aria-label={item.label}
                />
              </div>
            ))}
          </div>
        </section>

        {/* ── Acciones ── */}
        <div className="flex gap-3 pt-2 border-t border-border">
          <Button onClick={handleSave} className="gap-2 min-w-[140px] bg-primary hover:bg-primary/90 text-primary-foreground" aria-live="polite">
            {saved ? <Check size={15} /> : null}
            {saved ? 'Cambios guardados' : 'Guardar cambios'}
          </Button>
          <Button
            onClick={resetSettings}
            variant="outline"
            className="gap-2 hover:bg-primary/10 hover:text-primary hover:border-primary/40"
          >
            <RotateCcw size={15} />
            Restablecer
          </Button>
        </div>

      </main>
    </>
  )
}
