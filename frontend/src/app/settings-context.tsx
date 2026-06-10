"use client"

import { createContext, useContext, useEffect, useState } from 'react'
import { UserSettings, DEFAULT_SETTINGS } from '@/types/settings'
import { COLOR_SCHEMES } from '@/config/color-schemes'

interface SettingsContextType {
  settings:       UserSettings
  updateSettings: (updates: Partial<UserSettings>) => void
  resetSettings:  () => void
  isLoading:      boolean
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings]   = useState<UserSettings>(DEFAULT_SETTINGS)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadSettings()
  }, [])

  useEffect(() => {
    if (!isLoading) {
      applyTheme()
      applyDensity()
      applyFontSize()
      applyAccessibility()
    }
  }, [settings, isLoading])

  // Escuchar cambios de preferencia del sistema en tiempo real
  useEffect(() => {
    if (settings.themeMode !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => applyTheme()
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [settings.themeMode, settings.colorScheme])

  const loadSettings = () => {
    try {
      const stored = localStorage.getItem('userSettings')
      if (stored) {
        const parsed = JSON.parse(stored)
        setSettings({ ...DEFAULT_SETTINGS, ...parsed })
      }
    } catch (error) {
      console.error('Error loading settings:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const updateSettings = (updates: Partial<UserSettings>) => {
    setSettings(prev => {
      const newSettings = { ...prev, ...updates }
      localStorage.setItem('userSettings', JSON.stringify(newSettings))
      return newSettings
    })
  }

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
    localStorage.setItem('userSettings', JSON.stringify(DEFAULT_SETTINGS))
  }

  /**
   * applyTheme — arquitectura correcta:
   *
   *   1. El modo (light/dark) controla las superficies via clase CSS (.dark)
   *      → globals.css define los tokens de superficie en :root y .dark
   *
   *   2. El esquema controla solo los tokens de marca (primary, ring, charts)
   *      → Se aplican DESPUÉS del modo para no pisar las superficies
   *
   * Resultado: dark + "Esmeralda" = fondo oscuro con primary esmeralda ✓
   *            light + "Esmeralda" = fondo claro con primary esmeralda ✓
   */
  const applyTheme = () => {
    const root = document.documentElement
    const scheme = COLOR_SCHEMES[settings.colorScheme] ?? COLOR_SCHEMES['indigo']

    // 1. Aplicar modo (controla superficies)
    const isDark =
      settings.themeMode === 'dark' ||
      (settings.themeMode === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)

    root.classList.toggle('dark', isDark)

    // 2. Aplicar tokens de marca según modo
    const brandTokens = isDark ? scheme.darkColors : scheme.colors
    Object.entries(brandTokens).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value)
    })
  }

  const applyDensity = () => {
    const root = document.documentElement
    const densityMap: Record<string, string> = {
      compact:     '0.875rem',
      comfortable: '1rem',
      spacious:    '1.25rem',
    }
    root.style.setProperty('--spacing-unit', densityMap[settings.density])
  }

  const applyFontSize = () => {
    const root = document.documentElement
    const fontSizeMap: Record<string, string> = {
      small:  '14px',
      medium: '16px',
      large:  '18px',
    }
    root.style.setProperty('--base-font-size', fontSizeMap[settings.fontSize])
  }

  const applyAccessibility = () => {
    const root = document.documentElement

    // Movimiento reducido
    const noMotion = settings.reducedMotion || !settings.showAnimations
    root.style.setProperty('--animation-duration', noMotion ? '0s' : '0.15s')

    // Alto contraste — aplica un tema completo, no solo un filtro
    root.classList.toggle('high-contrast', settings.highContrast)
  }

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, resetSettings, isLoading }}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings must be used within SettingsProvider')
  }
  return context
}
