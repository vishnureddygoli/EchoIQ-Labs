export type Lead = { id: string; name?: string; phone: string; city?: string; source_platform: string; duplicate_status: string; compliance_status: string; created_at: string; score?: number; lead_temperature?: string };
export type DashboardMetrics = { api_available: boolean; error_message?: string; total_leads: number; queued_calls: number; hot_leads: number; new_leads: number; recent_leads: Lead[] };

const fallbackData = {
  total_leads: 1,
  queued_calls: 1,
  hot_leads: 1,
  new_leads: 1,
  recent_leads: [{ id: 'mock', name: 'Mock Lead', phone: '+15125550123', city: 'Austin', source_platform: 'website', duplicate_status: 'new', compliance_status: 'callable', created_at: new Date().toISOString(), score: 10, lead_temperature: 'new' }]
};

function unavailable(errorMessage: string): DashboardMetrics {
  return { api_available: false, error_message: errorMessage, ...fallbackData };
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${baseUrl}/leads/metrics/summary`, { cache: 'no-store' });
    if (!res.ok) return unavailable(`API returned ${res.status}`);
    const data = await res.json();
    return { api_available: true, ...data };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown API error';
    return unavailable(message);
  }
}
