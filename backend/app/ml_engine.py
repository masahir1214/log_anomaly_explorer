import pandas as pd
from sklearn.ensemble import IsolationForest
import networkx as nx
import json
import csv

def process_logs_pipeline(log_lines, filename=""):
    data = []
    
    # Dual-Format Parsing (JSON & CSV)
    if filename.lower().endswith('.csv'):
        reader = csv.DictReader(log_lines)
        for row in reader:
            data.append(row)
    else:
        for line in log_lines:
            try:
                parsed = json.loads(line)
                data.append(parsed)
            except:
                continue
            
    if not data:
        raise ValueError("No valid logs found. Please check file format.")
        
    df = pd.DataFrame(data)
    
    # Strip hidden whitespace from headers
    df.columns = df.columns.str.strip()
    
    # Ensure required columns
    if 'service' not in df.columns: df['service'] = 'unknown_service'
    if 'severity' not in df.columns: df['severity'] = 'INFO'
    if 'message' not in df.columns: df['message'] = ''
    if 'trace_id' not in df.columns: df['trace_id'] = 'none'

    # Feature Engineering
    sev_map = {'INFO': 1, 'WARN': 2, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4, 'FATAL': 5}
    df['sev_num'] = df['severity'].astype(str).str.upper().map(sev_map).fillna(1)
    df['msg_length'] = df['message'].astype(str).apply(len)

    # ML Anomaly Detection
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[['sev_num', 'msg_length']])
    
    anomalies = df[df['anomaly_score'] == -1]
    
    # NetworkX Graph Topology
    G = nx.Graph()
    for service in df['service'].unique():
        sev_max = df[df['service'] == service]['sev_num'].max()
        severity_label = "CRITICAL" if sev_max >= 4 else "HIGH" if sev_max == 3 else "MEDIUM" if sev_max == 2 else "LOW"
        ano_count = len(anomalies[anomalies['service'] == service])
        G.add_node(service, severity=severity_label, max_score=float(sev_max/5.0), anomaly_count=ano_count)

    traces = df[df['trace_id'] != 'none'].groupby('trace_id')['service'].unique()
    for trace_services in traces:
        for i in range(len(trace_services)):
            for j in range(i+1, len(trace_services)):
                G.add_edge(trace_services[i], trace_services[j])

    nodes = []
    for i, (node, n_data) in enumerate(G.nodes(data=True)):
        nodes.append({
            "id": str(node),
            "data": {"label": str(node), "severity": n_data.get("severity", "LOW"), "max_score": n_data.get("max_score", 0.0), "anomaly_count": n_data.get("anomaly_count", 0)},
            "position": {"x": 100 + (i * 150), "y": 100 + ((i % 2) * 100)}
        })
        
    edges = []
    for i, (u, v) in enumerate(G.edges()):
        edges.append({
            "id": f"e_{i}", "source": str(u), "target": str(v), "label": "TRACE", "data": {"type": "TRACE", "confidence": 0.85}
        })

    incident_title = "CRITICAL: Widespread Anomaly Detected" if len(anomalies) > 5 else "HIGH: Service Degradation"
    overall_severity = "CRITICAL" if len(anomalies) > 5 else "HIGH"
    
    # Safe Extraction (Prevents KeyError if columns are missing)
    valid_cols = [c for c in ['timestamp', 'service', 'severity', 'message'] if c in anomalies.columns]
    
    return {
        "title": incident_title,
        "severity": overall_severity,
        "service_count": len(G.nodes()),
        "anomaly_count": len(anomalies),
        "graph_data": {"nodes": nodes, "edges": edges},
        "raw_anomalies": anomalies[valid_cols].to_dict(orient='records')
    }
