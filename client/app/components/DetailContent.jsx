function DetailContent({ item }) {
  React.useEffect(() => {
    const container = document.getElementById('detailContent');
    if (!item) { container.innerHTML = '<div class="text-muted">No item selected</div>'; return; }
    const images = [item.image1_url, item.image2_url, item.image3_url, item.image4_url].filter(Boolean);
    const imagesHtml = images.map((src) => `<img src="${src}" class="img-fluid rounded me-2 mb-2" style="max-height:200px; object-fit:cover;"/>`).join('');
    container.innerHTML = `
      <div class="d-flex flex-column gap-2">
        <div>
          <div class="fw-semibold">${item.common_name || ''}</div>
          <div class="text-muted small">${item.botanical_name || ''}</div>
        </div>
        <div class="small">${item.description || ''}</div>
        <div class="d-flex flex-wrap">${imagesHtml}</div>
        ${item.url ? `<a class="small" href="${item.url}" target="_blank" rel="noreferrer">Source</a>` : ''}
      </div>
    `;
  }, [item]);
  return null;
}


