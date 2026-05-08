import Link from 'next/link'

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-gabon-500">GABOPAY</span>
            <span className="text-sm text-gray-500">Docs</span>
          </div>
          <nav className="flex gap-6 text-sm">
            <Link href="/docs" className="text-gray-600 hover:text-gabon-500">Home</Link>
            <Link href="/docs/quickstart" className="text-gray-600 hover:text-gabon-500">Quickstart</Link>
            <Link href="/docs/api" className="text-gray-600 hover:text-gabon-500">API Reference</Link>
            <Link href="/docs/guides" className="text-gray-600 hover:text-gabon-500">Guides</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Payment Infrastructure for Africa
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Integrate Airtel Money, Moov Money, and card payments into your application with a single API.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quickstart</h3>
            <p className="text-gray-600 mb-4">Get started in 5 minutes with your first payment.</p>
            <Link href="/docs/quickstart" className="text-gabon-500 font-medium hover:underline">
              Start integrating →
            </Link>
          </div>
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">API Reference</h3>
            <p className="text-gray-600 mb-4">Complete reference for all API endpoints.</p>
            <Link href="/docs/api" className="text-gabon-500 font-medium hover:underline">
              View API docs →
            </Link>
          </div>
          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">SDKs</h3>
            <p className="text-gray-600 mb-4">Official SDKs for JavaScript, Python, and Flutter.</p>
            <Link href="/docs/sdks" className="text-gabon-500 font-medium hover:underline">
              Install SDKs →
            </Link>
          </div>
        </div>

        <div className="bg-gabon-50 rounded-lg p-8 mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Supported Payment Methods</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900">Airtel Money</h3>
              <p className="text-sm text-gray-600">Gabon's leading mobile money service</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Moov Money</h3>
              <p className="text-sm text-gray-600">Secure mobile payments across Gabon</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Card Payments</h3>
              <p className="text-sm text-gray-600">VISA, Mastercard via CinetPay</p>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Code Example</h2>
          <pre className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto">
{`// Create a payment charge
const charge = await gp.charges.create({
  amount: 5000,        // 5,000 XAF
  currency: 'XAF',
  method: 'airtel_money',
  phone: '+24177000000',
  description: 'Order #123'
});

console.log(charge.status); // 'succeeded' | 'pending' | 'failed'`}
          </pre>
        </div>
      </main>
    </div>
  )
}