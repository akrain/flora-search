function ResultCard({ item, onClick }) {
  const images = [item.image1_url, item.image2_url, item.image3_url, item.image4_url].filter(Boolean);
  const imgSrc = images[0] || 'data:image/svg+xml;utf8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="100%" height="100%" fill="#e9ecef"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#6c757d" font-family="sans-serif" font-size="20">No Image</text></svg>`);
  return (
    <div className="col-6 col-sm-4 col-md-3 col-lg-2 mb-3">
      <div className="card h-100" role="button" onClick={() => onClick(item)}>
        <img className="thumb" src={imgSrc} alt={item.common_name || 'Flower'} loading="lazy" />
        <div className="card-body p-2">
          <div className="card-title text-truncate" title={item.common_name || ''}>{item.common_name || 'Unknown'}</div>
        </div>
      </div>
    </div>
  );
}


