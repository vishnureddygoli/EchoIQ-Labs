import { fetchDashboardMetrics } from '../lib/api';

export default async function Page() {
  const metrics = await fetchDashboardMetrics();
  const cards = [
    ['Total leads', metrics.total_leads],
    ['Queued calls', metrics.queued_calls],
    ['Hot leads', metrics.hot_leads],
    ['New leads', metrics.new_leads],
  ];
  return <main style={{ fontFamily: 'sans-serif', padding: 32 }}>
    <h1>EchoIQ Labs Revenue Recovery</h1>
    <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(140px, 1fr))', gap: 16 }}>
      {cards.map(([label, value]) => <div key={label} style={{ border: '1px solid #ddd', padding: 16, borderRadius: 8 }}><p>{label}</p><strong style={{ fontSize: 28 }}>{value}</strong></div>)}
    </section>
    <h2>Recent leads</h2>
    <table cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead><tr><th align="left">Name</th><th align="left">Phone</th><th align="left">City</th><th align="left">Source</th><th align="left">Status</th><th align="left">Score</th></tr></thead>
      <tbody>{metrics.recent_leads.map((lead) => <tr key={lead.id} style={{ borderTop: '1px solid #eee' }}><td>{lead.name || '—'}</td><td>{lead.phone}</td><td>{lead.city || '—'}</td><td>{lead.source_platform}</td><td>{lead.compliance_status}</td><td>{lead.score ?? '—'}</td></tr>)}</tbody>
    </table>
  </main>;
}
