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
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}