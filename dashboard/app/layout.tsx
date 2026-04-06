import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Trend Arbitrage Scout',
  description: 'Dashboard de tendências EUA → Brasil',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
