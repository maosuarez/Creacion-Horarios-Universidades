export type ThemeMode = 'light' | 'dark' | 'system'

/** Claves de esquemas de color disponibles en color-schemes.ts */
export type ColorScheme = 'indigo' | 'emerald' | 'amber' | 'rose' | 'sky' | 'violet'

export type FontSize = 'small' | 'medium' | 'large'
export type Density  = 'compact' | 'comfortable' | 'spacious'

export interface UserSettings {
  // Apariencia
  themeMode:    ThemeMode
  colorScheme:  ColorScheme
  fontSize:     FontSize
  density:      Density

  // Preferencias de UI
  showAnimations: boolean
  reducedMotion:  boolean
  highContrast:   boolean

  // Funcionalidades
  autoSaveSchedules: boolean
  defaultPageSize:   number
  language: 'es' | 'en'
}

export const DEFAULT_SETTINGS: UserSettings = {
  themeMode:    'system',
  colorScheme:  'indigo',   // índigo por defecto — profesional
  fontSize:     'medium',
  density:      'comfortable',
  showAnimations:    true,
  reducedMotion:     false,
  highContrast:      false,
  autoSaveSchedules: true,
  defaultPageSize:   10,
  language:          'es',
}
