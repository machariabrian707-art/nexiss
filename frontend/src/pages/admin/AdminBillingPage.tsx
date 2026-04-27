export default function AdminBillingPage() {
  const plans = [
    { name: 'Free', orgs: 120, revenue: '$0', color: 'bg-gray-100 text-gray-700' },
    { name: 'Starter', orgs: 340, revenue: '$6,800', color: 'bg-blue-100 text-blue-700' },
    { name: 'Pro', orgs: 87, revenue: '$26,100', color: 'bg-purple-100 text-purple-700' },
    { name: 'Enterprise', orgs: 12, revenue: '$60,000', color: 'bg-green-100 text-green-700' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Billing Overview</h1>
        <p className="text-sm text-gray-500 mt-1">Revenue and subscription breakdown across all organisations</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((p) => (
          <div key={p.name} className="card p-5">
            <span className={`badge mb-3 ${p.color}`}>{p.name}</span>
            <p className="text-xl font-bold text-gray-900">{p.orgs} orgs</p>
            <p className="text-sm text-gray-500">{p.revenue} / month</p>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <h2 className="font-semibold text-gray-800 mb-4">Stripe Integration</h2>
        <p className="text-sm text-gray-500 mb-4">
          Billing is managed via Stripe. Connect your Stripe account in environment config to enable
          live subscription management, invoicing, and usage-based billing.
        </p>
        <div className="bg-gray-50 rounded-xl p-4 font-mono text-xs text-gray-600">
          STRIPE_SECRET_KEY=sk_live_...<br />
          STRIPE_WEBHOOK_SECRET=whsec_...
        </div>
      </div>
    </div>
  )
}
