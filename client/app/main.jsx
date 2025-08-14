function useModal() {
  const [modal, setModal] = React.useState(null);
  React.useEffect(() => {
    const el = document.getElementById('detailModal');
    setModal(new bootstrap.Modal(el));
  }, []);
  return modal;
}

function App() {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [selected, setSelected] = React.useState(null);
  const [queryImageUrl, setQueryImageUrl] = React.useState(null);
  const modal = useModal();

  const openDetail = (item) => {
    setSelected(item);
    if (modal) modal.show();
  };

  const onSearch = async ({ text, file }) => {
    setLoading(true); setError(null);
    try {
      // Manage object URL for the uploaded image so we can show it in details
      if (file) {
        const url = URL.createObjectURL(file);
        setQueryImageUrl(url);
      } else {
        setQueryImageUrl(null);
      }
      const results = await searchFlowers({ text, file });
      setItems(results);
    } catch (e) {
      setError(e.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  // Revoke previous object URL when it changes or on unmount to avoid memory leaks
  React.useEffect(() => {
    return () => {
      if (queryImageUrl) URL.revokeObjectURL(queryImageUrl);
    };
  }, [queryImageUrl]);

  const onClear = () => {
    if (queryImageUrl) {
      URL.revokeObjectURL(queryImageUrl);
    }
    setQueryImageUrl(null);
    setError(null);
  };

  return (
    <div>
      <SearchForm onSearch={onSearch} loading={loading} onClear={onClear} />
      {queryImageUrl && (
        <div className="mb-3 d-flex justify-content-center">
          <div className="w-100" style={{ maxWidth: '640px' }}>
            <img
              src={queryImageUrl}
              alt="Uploaded"
              className="img-fluid rounded d-block mx-auto"
              style={{ maxHeight: '240px', maxWidth: '100%', width: 'auto', height: 'auto', objectFit: 'contain' }}
            />
            <div className="small text-muted mt-1 text-center">Uploaded image</div>
          </div>
        </div>
      )}
      {error && <div className="alert alert-danger py-2">{error}</div>}
      <div className="row">
        {items.map((item) => (
          <ResultCard key={(item.common_name || '') + (item.botanical_name || '')} item={item} onClick={openDetail} />
        ))}
      </div>

      {/* Modal content */}
      <DetailContent item={selected} queryImageUrl={queryImageUrl} />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(<App />);


