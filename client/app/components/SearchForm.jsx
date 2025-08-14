function SearchForm({ onSearch, loading, onClear }) {
  const [text, setText] = React.useState("");
  const [file, setFile] = React.useState(null);
  const [localError, setLocalError] = React.useState(null);
  const fileInputRef = React.useRef(null);
  const barRef = React.useRef(null);

  React.useEffect(() => {
    const bar = barRef.current;
    if (!bar) return;
    const onDragOver = (e) => { e.preventDefault(); bar.classList.add('dragover'); };
    const onDragLeave = () => bar.classList.remove('dragover');
    const onDrop = (e) => {
      e.preventDefault(); bar.classList.remove('dragover');
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) handleFileSelection(f);
    };
    bar.addEventListener('dragover', onDragOver);
    bar.addEventListener('dragleave', onDragLeave);
    bar.addEventListener('drop', onDrop);
    return () => {
      bar.removeEventListener('dragover', onDragOver);
      bar.removeEventListener('dragleave', onDragLeave);
      bar.removeEventListener('drop', onDrop);
    };
  }, [onSearch, text]);

  const onKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      onSearch({ text, file });
    }
  };

  const onSelectFile = (evt) => {
    const f = evt.target.files && evt.target.files[0];
    if (f) handleFileSelection(f);
  };

  const clearFile = () => {
    setFile(null);
    setText("");
    if (fileInputRef.current) fileInputRef.current.value = "";
    setLocalError(null);
    if (typeof onClear === 'function') onClear();
  };

  const handleFileSelection = (f) => {
    const MAX_SIZE = 2 * 1024 * 1024; // 4 MB
    const allowedTypes = ["image/jpeg", "image/png"]; 
    const name = (f.name || "").toLowerCase();
    const typeOk = allowedTypes.includes(f.type) || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".png");
    const sizeOk = typeof f.size === 'number' ? f.size <= MAX_SIZE : true;

    if (!typeOk || !sizeOk) {
      const reason = !typeOk ? "Only JPEG and PNG images are allowed." : "Image must be 4MB or smaller.";
      setLocalError(reason);
      return;
    }

    setLocalError(null);
    setFile(f);
    onSearch({ text, file: f });
  };

  return (
    <div className="mb-4 d-flex justify-content-center">
      <div className="w-100" style={{ maxWidth: '640px' }}>
        <div className="search-bar" ref={barRef}>
          <span className="leading-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </span>
          <input
            type="text"
            className="search-input"
            placeholder="Search flowers (e.g., rose, orchid)"
            value={file ? file.name : text}
            disabled={!!file}
            onChange={(e) => { if (!file) setText(e.target.value); }}
            onKeyDown={onKeyDown}
            title={file ? file.name : undefined}
            aria-disabled={!!file}
          />
          <div className="trailing-actions">
            {file && (
              <button type="button" className="icon-btn" aria-label="Clear image" title="Clear image" onClick={clearFile}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            )}
            <button type="button" className="icon-btn" aria-label="Upload image" title="Upload image" onClick={() => fileInputRef.current && fileInputRef.current.click()}>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </button>
          </div>
          <input
            type="file"
            accept="image/jpeg,image/png"
            className="d-none"
            ref={fileInputRef}
            onChange={onSelectFile}
          />
        </div>
        {localError && (
          <div className="text-danger small mt-2" role="alert">{localError}</div>
        )}
      </div>
    </div>
  );
}


