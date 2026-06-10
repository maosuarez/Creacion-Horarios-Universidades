"use client"

import { useAuth } from "@/app/auth-context"
import { Navbar } from "@/components/navbar"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { CalendarDays, SlidersHorizontal, Download } from "lucide-react"

export default function Home() {
  const { user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (user) {
      router.push("/dashboard")
    }
  }, [user, router])

  return (
    <>
      <Navbar />
      <main className="min-h-[calc(100vh-3.5rem)]">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-20 text-center space-y-8">

          {/* Propuesta de valor — clara, sin adorno */}
          <div className="space-y-4">
            <h1 className="text-4xl sm:text-5xl font-bold text-foreground tracking-tight">
              Tu horario universitario,<br />
              <span className="text-primary">sin el caos</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              Elige tus materias, profesores preferidos y horas libres.
              Nosotros generamos todas las combinaciones posibles.
            </p>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/signup">
              <Button size="lg" className="w-full sm:w-auto px-8">
                Crear cuenta gratis
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto px-8">
                Iniciar sesión
              </Button>
            </Link>
          </div>

          {/* Beneficios — concretos */}
          <div className="grid sm:grid-cols-3 gap-4 pt-8 text-left">
            {[
              {
                icon: <CalendarDays size={20} className="text-primary" />,
                title: "Todas las opciones",
                desc: "Genera automáticamente cada combinación válida sin conflictos.",
              },
              {
                icon: <SlidersHorizontal size={20} className="text-primary" />,
                title: "A tu medida",
                desc: "Bloquea horas libres, filtra por profesor y elige secciones específicas.",
              },
              {
                icon: <Download size={20} className="text-primary" />,
                title: "Exporta en Excel",
                desc: "Descarga tu horario favorito listo para imprimir o compartir.",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="p-5 bg-card border border-border rounded-lg space-y-2 surface-elevated"
              >
                <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center">
                  {item.icon}
                </div>
                <h2 className="text-sm font-semibold text-foreground">{item.title}</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </main>
    </>
  )
}
