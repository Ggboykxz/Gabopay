import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'GABOPAY Dashboard',
  description: 'Payment Infrastructure for Gabon and Africa',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}