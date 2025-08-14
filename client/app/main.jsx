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
  const modal = useModal();

  const openDetail = (item) => {
    setSelected(item);
    if (modal) modal.show();
  };

  const onSearch = async ({ text, file }) => {
    setLoading(true); setError(null);
    try {
      const results = await searchFlowers({ text, file });
      setItems(results);
    } catch (e) {
      setError(e.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <SearchForm onSearch={onSearch} loading={loading} />
      {error && <div className="alert alert-danger py-2">{error}</div>}
      <div className="row">
        {items.map((item) => (
          <ResultCard key={(item.common_name || '') + (item.botanical_name || '')} item={item} onClick={openDetail} />
        ))}
      </div>

      {/* Modal content */}
      <DetailContent item={selected} />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(<App />);


