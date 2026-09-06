type Incident = Record<string, unknown>;
type GraphData = Record<string, unknown>;

const API_BASE = '/api';

export const api = {
  uploadLogs: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/logs/upload`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },
  getIncidents: async (): Promise<Incident[]> => {
    const res = await fetch(`${API_BASE}/incidents`);
    if (!res.ok) return [];
    return res.json();
  },
  getIncidentGraph: async (id: number): Promise<GraphData> => {
    const res = await fetch(`${API_BASE}/incidents/${id}/graph`);
    if (!res.ok) throw new Error('Failed to load graph');
    return res.json();
  },
  getRca: async (id: number) => {
    const res = await fetch(`${API_BASE}/incidents/${id}/rca`, { method: 'POST' });
    if (!res.ok) throw new Error('RCA failed');
    return res.json();
  }
};