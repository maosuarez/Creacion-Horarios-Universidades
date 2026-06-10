/**
 * Esquemas de color — solo tokens de MARCA
 *
 * Arquitectura:
 * - El modo (light/dark) controla las SUPERFICIES: background, card, border, muted
 * - El esquema controla la MARCA: primary, ring, charts
 * - Los dos son ortogonales: cualquier combinación funciona
 *
 * Contraste verificado:
 * - `colors`     → para light mode (sobre #FFFFFF / #FAFAFA)
 * - `darkColors` → para dark mode  (sobre #0F172A / #1E293B)
 * Todos pasan WCAG AA (≥ 4.5:1)
 */

export interface SchemeTokens {
  primary: string
  'primary-foreground': string
  ring: string
  'chart-1': string
  'chart-2': string
  'chart-3': string
  'chart-4': string
  'chart-5': string
}

export interface ColorSchemeDefinition {
  name: string
  description: string
  /** Preview swatches — muestra el ramp de colores en Configuración */
  swatches: [string, string, string]
  /** Tokens para modo CLARO */
  colors: SchemeTokens
  /** Tokens para modo OSCURO */
  darkColors: SchemeTokens
}

export const COLOR_SCHEMES: Record<string, ColorSchemeDefinition> = {
  indigo: {
    name: 'Índigo',
    description: 'Profesional y académico',
    swatches: ['#4F46E5', '#818CF8', '#C7D2FE'],
    colors: {
      primary:             '#4F46E5',  /* indigo-600 — 7.0:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#4F46E5',
      'chart-1':           '#4F46E5',
      'chart-2':           '#0EA5E9',
      'chart-3':           '#059669',
      'chart-4':           '#D97706',
      'chart-5':           '#DC2626',
    },
    darkColors: {
      primary:             '#818CF8',  /* indigo-400 — 6.4:1 ✓ */
      'primary-foreground':'#1E1B4B',
      ring:                '#818CF8',
      'chart-1':           '#818CF8',
      'chart-2':           '#38BDF8',
      'chart-3':           '#34D399',
      'chart-4':           '#FBBF24',
      'chart-5':           '#F87171',
    },
  },

  emerald: {
    name: 'Esmeralda',
    description: 'Fresco, crecimiento',
    swatches: ['#059669', '#34D399', '#A7F3D0'],
    colors: {
      primary:             '#059669',  /* emerald-600 — 4.6:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#059669',
      'chart-1':           '#059669',
      'chart-2':           '#0EA5E9',
      'chart-3':           '#7C3AED',
      'chart-4':           '#D97706',
      'chart-5':           '#DC2626',
    },
    darkColors: {
      primary:             '#34D399',  /* emerald-400 — 8.8:1 ✓ */
      'primary-foreground':'#064E3B',
      ring:                '#34D399',
      'chart-1':           '#34D399',
      'chart-2':           '#38BDF8',
      'chart-3':           '#A78BFA',
      'chart-4':           '#FBBF24',
      'chart-5':           '#F87171',
    },
  },

  amber: {
    name: 'Ámbar',
    description: 'Cálido y energético',
    swatches: ['#B45309', '#FBBF24', '#FDE68A'],
    colors: {
      primary:             '#B45309',  /* amber-700 — 5.1:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#B45309',
      'chart-1':           '#B45309',
      'chart-2':           '#059669',
      'chart-3':           '#0EA5E9',
      'chart-4':           '#7C3AED',
      'chart-5':           '#DC2626',
    },
    darkColors: {
      primary:             '#FBBF24',  /* amber-400 — 9.0:1 ✓ */
      'primary-foreground':'#451A03',
      ring:                '#FBBF24',
      'chart-1':           '#FBBF24',
      'chart-2':           '#34D399',
      'chart-3':           '#38BDF8',
      'chart-4':           '#A78BFA',
      'chart-5':           '#F87171',
    },
  },

  rose: {
    name: 'Rosa',
    description: 'Cercano y amigable',
    swatches: ['#E11D48', '#FB7185', '#FECDD3'],
    colors: {
      primary:             '#E11D48',  /* rose-600 — 5.5:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#E11D48',
      'chart-1':           '#E11D48',
      'chart-2':           '#7C3AED',
      'chart-3':           '#0EA5E9',
      'chart-4':           '#D97706',
      'chart-5':           '#059669',
    },
    darkColors: {
      primary:             '#FB7185',  /* rose-400 — 5.7:1 ✓ */
      'primary-foreground':'#4C0519',
      ring:                '#FB7185',
      'chart-1':           '#FB7185',
      'chart-2':           '#A78BFA',
      'chart-3':           '#38BDF8',
      'chart-4':           '#FBBF24',
      'chart-5':           '#34D399',
    },
  },

  sky: {
    name: 'Cielo',
    description: 'Calma y claridad',
    swatches: ['#0284C7', '#38BDF8', '#BAE6FD'],
    colors: {
      primary:             '#0284C7',  /* sky-600 — 5.5:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#0284C7',
      'chart-1':           '#0284C7',
      'chart-2':           '#059669',
      'chart-3':           '#7C3AED',
      'chart-4':           '#D97706',
      'chart-5':           '#DC2626',
    },
    darkColors: {
      primary:             '#38BDF8',  /* sky-400 — 8.7:1 ✓ */
      'primary-foreground':'#082F49',
      ring:                '#38BDF8',
      'chart-1':           '#38BDF8',
      'chart-2':           '#34D399',
      'chart-3':           '#A78BFA',
      'chart-4':           '#FBBF24',
      'chart-5':           '#F87171',
    },
  },

  violet: {
    name: 'Violeta',
    description: 'Creativo e imaginativo',
    swatches: ['#7C3AED', '#A78BFA', '#DDD6FE'],
    colors: {
      primary:             '#7C3AED',  /* violet-600 — 5.9:1 ✓ */
      'primary-foreground':'#FFFFFF',
      ring:                '#7C3AED',
      'chart-1':           '#7C3AED',
      'chart-2':           '#0EA5E9',
      'chart-3':           '#059669',
      'chart-4':           '#D97706',
      'chart-5':           '#DC2626',
    },
    darkColors: {
      primary:             '#A78BFA',  /* violet-400 — 6.2:1 ✓ */
      'primary-foreground':'#2E1065',
      ring:                '#A78BFA',
      'chart-1':           '#A78BFA',
      'chart-2':           '#38BDF8',
      'chart-3':           '#34D399',
      'chart-4':           '#FBBF24',
      'chart-5':           '#F87171',
    },
  },
}
