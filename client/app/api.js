const API_BASE = (window.FLORA_API_BASE || "http://localhost:8000").replace(/\/$/, "");

async function searchFlowers({ text, file }) {
  const form = new FormData();
  if (text) form.append('q', text);
  if (file) form.append('q_img', file);
  const res = await fetch(`${API_BASE}/flowers/search/`, { method: 'POST', body: form });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if (data && typeof data.detail === 'string') message = data.detail;
    } catch (_) {}
    throw new Error(message);
  }
  const data = await res.json();
  return Array.isArray(data.items) ? data.items : [];
}


