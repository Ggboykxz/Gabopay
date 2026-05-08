export default function ApiReferencePage() {
  return (
    <div className="max-w-4xl mx-auto py-16 px-4">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">API Reference</h1>

      <div className="space-y-8">
        <section className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Authentication</h2>
          <p className="text-gray-600 mb-4">
            All API requests require an API key in the header. Get your keys from the dashboard.
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`curl -X GET https://api.gabopay.ga/v1/charges \\
  -H "X-API-Key: gp_test_sk_xxxxxxxx"`}
          </pre>
        </section>

        <section className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Create Charge</h2>
          <p className="text-gray-600 mb-4">Create a new payment charge.</p>
          <div className="mb-4">
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">POST</span>
            <span className="ml-2 text-gray-600 font-mono">/v1/charges</span>
          </div>

          <h3 className="font-medium text-gray-900 mb-2">Request Body</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`{
  "amount": 5000,
  "currency": "XAF",
  "method": "airtel_money",
  "phone": "+24177000000",
  "description": "Order #123",
  "metadata": {}
}`}
          </pre>

          <h3 className="font-medium text-gray-900 mb-2">Response</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`{
  "id": "ch_01J7XXXXX",
  "object": "charge",
  "amount": 5000,
  "currency": "XAF",
  "status": "succeeded",
  "method": "airtel_money",
  "created": 1720000000
}`}
          </pre>
        </section>

        <section className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Get Charge</h2>
          <p className="text-gray-600 mb-4">Retrieve a charge by ID.</p>
          <div className="mb-4">
            <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">GET</span>
            <span className="ml-2 text-gray-600 font-mono">/v1/charges/[id]</span>
          </div>
        </section>

        <section className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Create Refund</h2>
          <p className="text-gray-600 mb-4">Refund a successful charge.</p>
          <div className="mb-4">
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">POST</span>
            <span className="ml-2 text-gray-600 font-mono">/v1/refunds</span>
          </div>
        </section>

        <section className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Error Codes</h2>
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-900">Code</th>
                <th className="px-4 py-2 text-left font-medium text-gray-900">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-4 py-2 font-mono">insufficient_funds</td>
                <td className="px-4 py-2">The mobile money account has insufficient funds</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-mono">invalid_phone</td>
                <td className="px-4 py-2">The phone number is invalid</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-mono">timeout</td>
                <td className="px-4 py-2">The payment request timed out</td>
              </tr>
              <tr>
                <td className="px-4 py-2 font-mono">provider_error</td>
                <td className="px-4 py-2">The payment provider returned an error</td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}