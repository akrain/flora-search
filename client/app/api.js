const API_BASE = (window.FLORA_API_BASE || "http://localhost:8000").replace(/\/$/, "");

async function searchFlowers({ text, file }) {
  const form = new FormData();
  if (text) form.append('q', text);
  if (file) form.append('q_img', file);
  const res = await fetch(`${API_BASE}/flowers/search/`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data.items) ? data.items : [];
}


