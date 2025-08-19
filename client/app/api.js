const API_BASE = (window.FLORA_API_BASE || "http://localhost:8000").replace(/\/$/, "");

async function searchFlowers({ text, file }) {
  const form = new FormData();
  if (text) form.append('q', text);
  if (file) form.append('q_img', file);
  const res = await fetch(`${API_BASE}/flowers/search/`, { method: 'POST', body: form });
  const items = await res.json();
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    if (data && typeof data.detail === 'string') {
        message = data.detail;
    }
    throw new Error(message);
  }
  return items;
}


