"use client"

import { Navbar } from "@/components/navbar"
import { ProtectedRoute } from "@/components/protected-route"
import { ScheduleGenerator } from "@/components/schedule-generator"

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <Navbar />
      <main className="min-h-screen">
        <ScheduleGenerator />
      </main>
    </ProtectedRoute>
  )
}
