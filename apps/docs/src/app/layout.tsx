import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GABOPAY Documentation',
  description: 'Payment Infrastructure for Gabon and Africa - Developer Documentation',
}

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <style>{`
          body { margin: 0; font-family: system-ui, sans-serif; background: #f8f9fa; }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}