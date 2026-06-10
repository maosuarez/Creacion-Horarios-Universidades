"use client"

import { SettingsProvider } from "@/app/settings-context"
import { AuthProvider } from "@/app/auth-context"

export function Providers({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <AuthProvider>
      <SettingsProvider>{children}</SettingsProvider>
    </AuthProvider>
  )
}