import React, { useState, useEffect } from 'react';
import { ReactFlow, Controls, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const API_BASE = '/api';

export default function App() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<number | null>(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [rca, setRca] = useState<any>(null);
  const [uploading, setUploading] = useState(false);

  const fetchIncidents = async () => {
    const res = await fetch(`${API_BASE}/incidents`);
    if (res.ok) setIncidents(await res.json());
  };

  useEffect(() => { fetchIncidents(); }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await fetch(`${API_BASE}/logs/upload`, { method: 'POST', body: formData });
      if (res.ok) {
        alert('File successfully processed through Machine Learning Pipeline!');
        fetchIncidents();
      } else {
        alert('Upload failed. Check backend terminal for details.');
      }
    } catch(e) {
      alert('Error connecting to backend.');
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    if (selectedIncident) {
      fetch(`${API_BASE}/incidents/${selectedIncident}/graph`)
        .then(res => res.json())
        .then(data => {
            const formattedNodes = data.nodes.map((n: any) => ({
                id: n.id, position: n.position,
                data: { label: `${n.data.label}\nAnomalies: ${n.data.anomaly_count}` },
                style: { background: 'var(--panel)', color: 'var(--text)', border: `2px solid var(--${n.data.severity.toLowerCase()})`, borderRadius: 8, padding: 10, textAlign: 'center' }
            }));
            setGraphData({ nodes: formattedNodes, edges: data.edges });
            setRca(null);
        });
    }
  }, [selectedIncident]);

  const generateRCA = async () => {
    if (!selectedIncident) return;
    setRca({ root_cause: "Analyzing with AI...", confidence: "...", recommended_actions: [] });
    const res = await fetch(`${API_BASE}/incidents/${selectedIncident}/rca`, { method: 'POST' });
    if (res.ok) setRca(await res.json());
  };

  return (
    <div className="app-container">
      <div className="header">
        <div>
            <h1>Log Anomaly Explorer</h1>
            <p className="text-muted">Multi-Model Detection & AI Root Cause Analysis</p>
        </div>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <span style={{ fontWeight: 'bold' }}>Upload Real Logs:</span>
            <input type="file" accept=".json,.log,.txt,.csv" onChange={handleFileUpload} disabled={uploading} />
            {uploading && <span style={{ color: 'var(--accent)' }}>Processing ML...</span>}
        </div>
      </div>
      
      <div className="grid">
        <div className="panel">
            <h2>Detected Incidents</h2>
            {incidents.length === 0 ? <p className="text-muted">No incidents found. Upload a log file.</p> : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
                {incidents.map(inc => (
                <li key={inc.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--border)', cursor: 'pointer', background: selectedIncident === inc.id ? 'rgba(255,255,255,0.05)' : 'transparent' }} onClick={() => setSelectedIncident(inc.id)}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{inc.title}</strong><span className={`badge ${inc.severity}`}>{inc.severity}</span>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    Services affected: {inc.service_count} | Anomalies: {inc.anomaly_count}
                    </div>
                </li>
                ))}
            </ul>
            )}
        </div>

        <div>
            {selectedIncident ? (
                <>
                    <div className="panel" style={{ height: 350 }}>
                        <h2>Service Correlation Graph</h2>
                        <ReactFlow nodes={graphData.nodes} edges={graphData.edges} fitView>
                            <Background /><Controls />
                        </ReactFlow>
                    </div>
                    
                    <div className="panel">
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <h2>AI Root Cause Analysis</h2>
                            <button className="btn" onClick={generateRCA}>Run AI Analysis</button>
                        </div>
                        {rca && (
                            <div className="rca-box">
                                <h3 style={{marginTop: 0, color: 'var(--critical)'}}>Root Cause:</h3>
                                <p>{rca.root_cause}</p>
                                <h4>Recommended Actions:</h4>
                                <ul>{rca.recommended_actions.map((act: string, i: number) => <li key={i}>{act}</li>)}</ul>
                                <p className="text-muted" style={{fontSize: '0.8rem', marginTop: 10}}>Confidence: {rca.confidence*100} %</p>
                            </div>
                        )}
                    </div>
                </>
            ) : (
                <div className="panel" style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-muted)' }}>
                    <h2>Select an incident to view topology and generate RCA.</h2>
                </div>
            )}
        </div>
      </div>
    </div>
  );
}