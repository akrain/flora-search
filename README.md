## Flora Search

A simple end to end app to import a dataset of Himalayan flowers into ChromaDB and search semantically via text or
image.
I made it for identifying flowers photographed in the wild on my treks in the Himalaya.

### Acknowledgment

Uses data from the excellent [Flowers of India](https://www.flowersofindia.net) website.

### Prerequisites

- Python 3.11+ with virtualenv

Install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 1) Import data (scripts/import_data.py)

Imports a CSV into ChromaDB, optionally downloading remote images locally.

```bash
# Activate venv first
source .venv/bin/activate

# Basic usage (default CSV: foi_himalayan_flowers.csv)
cd scripts
python import_data.py

# With options
python import_data.py path/to/data.csv --start 0 --end 500 --no-download
```

Notes:

- Data is written into two collections: `flora_text` and `flora_images`.
- Downloaded images are saved to the `img/` folder.

### 2) Move images to server

Move the downloaded images to server source directory

```bash
mv scripts/img src/img
```

### 2) Run backend (FastAPI)

The backend exposes a search API that returns a list of Flower objects (as dicts).

```bash
source .venv/bin/activate
python -m src.main
```

Endpoints:

- `GET /` Hello world!
- `POST /flowers/search/` Form-data with either `q` (text) or `q_img` (image file, JPEG/PNG, max 2MB)

Environment/config:

- Chroma persistence path defaults to `src/chroma` (see `src/chroma.py`).

### 3) Frontend (client/app)

The frontend is a static app using React via CDN. Open `client/app/index.html` in a browser, or serve the `client/app/`
directory with any static file server.

```bash
# Example: Python simple server (do not use in production)
cd client/app
python -m http.server 5173
# Then visit http://localhost:5173
```

Config:

- Optional global `window.FLORA_API_BASE` can be set to point the client to a different API origin.

### Tests

```bash
source .venv/bin/activate
pytest
```


