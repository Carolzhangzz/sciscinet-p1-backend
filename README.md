
# SciSciNet Backend

Backend service for **SciSciNet**, a research network visualization system built on
publication metadata from **OpenAlex**.

This backend is responsible for **data acquisition, preprocessing, network construction,
and API delivery**, supporting interactive exploration of academic collaboration and
citation patterns in the frontend.

---

## Overview

The backend implements a complete data pipeline for research network visualization:

1. **Data Collection**
   - Downloads publication metadata from OpenAlex
   - Filters papers affiliated with **University of California, San Diego**
   - Focuses on the **Computer Science** field

2. **Data Processing & Network Construction**
   - Builds an **author collaboration network** based on co-authorship
   - Builds a **paper citation network** based on internal references
   - Normalizes data into JSON structures optimized for D3-based visualization

3. **API Service**
   - Exposes processed networks through a Flask REST API
   - Serves summary statistics and metadata for dashboards and interaction

This backend is designed to be modular and extensible, allowing additional institutions,
time ranges, or network types to be added with minimal changes.

---

## Project Structure

```

sciscinet-p1-backend/
├── app.py                          # Flask API server
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
└── scripts/
├── download_data.py            # Fetch data from OpenAlex API
├── build_author_network.py     # Construct author collaboration graph
├── build_citation_network.py   # Construct paper citation graph
└── data/
├── raw/                    # Raw OpenAlex responses
│   └── ucsd_papers.json
└── processed/              # Processed datasets for serving
├── papers.csv
├── authors.csv
├── paper_author_affiliations.csv
├── paper_references.csv
├── author_network.json
└── citation_network.json

````

---

## Data Pipeline

### Data Source
- **Provider**: OpenAlex
- **Institution**: University of California, San Diego
- **Field**: Computer Science
- **Time Range**: 2020–2025

### Processing Steps
- Retrieve publication metadata from OpenAlex
- Extract paper-level attributes (title, year, citation count)
- Resolve author identities and affiliations
- Construct:
  - Author collaboration edges weighted by co-authorship frequency
  - Paper citation edges representing internal references
- Export intermediate CSV files for transparency and debugging
- Export final network representations as JSON for API serving

---

## Setup

### Prerequisites
- Python 3.9+
- Virtual environment recommended

### Install Dependencies

```bash
pip install -r requirements.txt
````

---

## Data Preparation

```bash
cd scripts

# Download raw data from OpenAlex
python download_data.py

# Build author collaboration network
python build_author_network.py

# Build paper citation network
python build_citation_network.py

cd ..
```

> Note: Downloading data from OpenAlex may take several minutes depending on network conditions.

---

## Running the API Server

```bash
python app.py
```

The server starts at:

```
http://localhost:5001
```

CORS is enabled to support local frontend development.

---

## API Endpoints

### Base

* **GET** `/`
* Returns service status and available endpoints

---

### Author Collaboration Network

* **GET** `/api/author-network`
* Returns a node-link representation of co-authorship relationships

```json
{
  "nodes": [
    { "id": "A123", "name": "Author Name", "paperCount": 5 }
  ],
  "links": [
    { "source": "A123", "target": "A456", "weight": 2 }
  ],
  "metadata": { ... }
}
```

---

### Paper Citation Network

* **GET** `/api/citation-network`
* Returns internal citation relationships between papers

```json
{
  "nodes": [
    { "id": "W123", "title": "Paper Title", "year": 2023, "citationCount": 120 }
  ],
  "links": [
    { "source": "W123", "target": "W456" }
  ],
  "metadata": { ... }
}
```

---

### Statistics

* **GET** `/api/stats`
* Returns summary statistics for all networks

---

### Health Check

* **GET** `/health`
* Returns server health status

---

## Network Statistics (Current Dataset)

**Author Collaboration Network**

* Authors: 1,134
* Collaboration edges: 36,623
* Average collaborations per author pair: 1.16

**Citation Network**

* Papers: 69
* Internal citation links: 14
* Average citation count per paper: 645+

---

## Development Notes

* API responses are optimized for D3-based visualization
* CSV intermediates are retained for debugging and extensibility
* The data pipeline is modular and can be adapted to other institutions
  or research domains with minimal refactoring

---

## Author

**Carol Zhang**
M.S. in Computer Science, UC San Diego

---

## License

This project was developed as part of a **technical coding test** and is intended
for evaluation and demonstration purposes.

