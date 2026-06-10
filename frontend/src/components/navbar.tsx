"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/app/auth-context"
import { Button } from "@/components/ui/button"
import { Menu, X, LogOut, User, BookOpen, Settings, Users, Share2 } from "lucide-react"

export function Navbar() {
  const { user, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const pathname = usePathname()

  /**
   * Clases para ítems de nav.
   * Las variantes ghost/outline de shadcn tienen `hover:bg-accent hover:text-accent-foreground`
   * que twMerge resuelve correctamente cuando pasamos las clases después (className prop).
   * Añadimos hover:text-primary explícito en ambos estados para que el color
   * se mantenga correcto independientemente del valor de --accent.
   */
  const navCls = (href: string) =>
    pathname === href
      ? "gap-1.5 text-sm bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary"
      : "gap-1.5 text-sm text-foreground/70 hover:bg-primary/10 hover:text-primary"

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14">

          {/* Logotipo */}
          <Link
            href={user ? "/dashboard" : "/"}
            className="flex items-center gap-2 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
            aria-label="ScheduleMaster — ir al inicio"
          >
            <div
              className="w-8 h-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground font-bold text-sm select-none"
              aria-hidden="true"
            >
              S
            </div>
            <span className="font-semibold text-base text-foreground group-hover:text-primary transition-colors">
              ScheduleMaster
            </span>
          </Link>

          {/* Menú escritorio */}
          <div className="hidden md:flex items-center gap-1">
            {user ? (
              <>
                <span className="text-sm text-muted-foreground px-2 select-none">
                  Hola, {user.name}
                </span>

                {user.role === "creator" && (
                  <Link href="/courses">
                    <Button variant="ghost" size="sm" className={navCls("/courses")}>
                      <BookOpen size={15} aria-hidden="true" />
                      Materias
                    </Button>
                  </Link>
                )}

                {user.role === "creator" && (
                  <Link href="/admin/users">
                    <Button variant="ghost" size="sm" className={navCls("/admin/users")}>
                      <Users size={15} aria-hidden="true" />
                      Usuarios
                    </Button>
                  </Link>
                )}

                <Link href="/shared-schedules">
                  <Button variant="ghost" size="sm" className={navCls("/shared-schedules")}>
                    <Share2 size={15} aria-hidden="true" />
                    Compartidos
                  </Button>
                </Link>

                <Link href="/settings">
                  <Button variant="ghost" size="sm" className={navCls("/settings")}>
                    <Settings size={15} aria-hidden="true" />
                    Configuración
                  </Button>
                </Link>

                <Link href="/profile">
                  <Button variant="ghost" size="sm" className={navCls("/profile")}>
                    <User size={15} aria-hidden="true" />
                    Perfil
                  </Button>
                </Link>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="gap-1.5 text-sm text-destructive hover:text-destructive hover:bg-destructive/10 ml-1"
                >
                  <LogOut size={15} aria-hidden="true" />
                  Salir
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">Iniciar sesión</Button>
                </Link>
                <Link href="/signup">
                  <Button size="sm" className="ml-1">Registrarse</Button>
                </Link>
              </>
            )}
          </div>

          {/* Botón menú móvil */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2 rounded-md text-foreground hover:bg-muted transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Menú móvil */}
        {menuOpen && (
          <div
            className="md:hidden pb-3 border-t border-border pt-3 space-y-1"
            role="menu"
          >
            {user ? (
              <>
                <p className="px-3 py-1 text-sm text-muted-foreground">Hola, {user.name}</p>

                {user.role === "creator" && (
                  <Link href="/courses" onClick={() => setMenuOpen(false)}>
                    <Button variant="ghost" className={`w-full justify-start ${navCls("/courses")}`} role="menuitem">
                      <BookOpen size={15} /> Materias
                    </Button>
                  </Link>
                )}

                {user.role === "creator" && (
                  <Link href="/admin/users" onClick={() => setMenuOpen(false)}>
                    <Button variant="ghost" className={`w-full justify-start ${navCls("/admin/users")}`} role="menuitem">
                      <Users size={15} /> Usuarios
                    </Button>
                  </Link>
                )}

                <Link href="/shared-schedules" onClick={() => setMenuOpen(false)}>
                  <Button variant="ghost" className={`w-full justify-start ${navCls("/shared-schedules")}`} role="menuitem">
                    <Share2 size={15} /> Compartidos
                  </Button>
                </Link>

                <Link href="/settings" onClick={() => setMenuOpen(false)}>
                  <Button variant="ghost" className={`w-full justify-start ${navCls("/settings")}`} role="menuitem">
                    <Settings size={15} /> Configuración
                  </Button>
                </Link>

                <Link href="/profile" onClick={() => setMenuOpen(false)}>
                  <Button variant="ghost" className={`w-full justify-start ${navCls("/profile")}`} role="menuitem">
                    <User size={15} /> Perfil
                  </Button>
                </Link>

                <Button
                  variant="ghost"
                  onClick={() => { logout(); setMenuOpen(false) }}
                  className="w-full justify-start gap-2 text-sm text-destructive hover:text-destructive hover:bg-destructive/10"
                  role="menuitem"
                >
                  <LogOut size={15} /> Salir
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMenuOpen(false)}>
                  <Button variant="ghost" className="w-full justify-start text-sm" role="menuitem">
                    Iniciar sesión
                  </Button>
                </Link>
                <Link href="/signup" onClick={() => setMenuOpen(false)}>
                  <Button className="w-full text-sm" role="menuitem">
                    Registrarse
                  </Button>
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
