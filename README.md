# SciSciNet Backend

Backend API for SciSciNet visualization project using UCSD CS papers data from OpenAlex.

## Project Structure

```
sciscinet-p1-backend/
├── app.py                          # Flask API server
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── scripts/
    ├── download_data.py           # Download data from OpenAlex API
    ├── build_author_network.py    # Build author collaboration network
    ├── build_citation_network.py  # Build paper citation network
    └── data/
        ├── raw/                   # Raw data from OpenAlex
        │   └── ucsd_papers.json
        └── processed/             # Processed data
            ├── papers.csv
            ├── authors.csv
            ├── paper_author_affiliations.csv
            ├── paper_references.csv
            ├── author_network.json
            └── citation_network.json
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download and Process Data

```bash
# Navigate to scripts directory
cd scripts

# Download data from OpenAlex (this will take a few minutes)
python download_data.py

# Build author collaboration network
python build_author_network.py

# Build paper citation network
python build_citation_network.py

# Return to root directory
cd ..
```

## Running the API Server

```bash
# Start the Flask server
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Home
- **GET** `/`
- Returns API information and available endpoints

### 2. Author Collaboration Network
- **GET** `/api/author-network`
- Returns the author collaboration network data (nodes and links)
- Response format:
```json
{
  "nodes": [
    {"id": "123", "name": "Author Name", "paperCount": 5}
  ],
  "links": [
    {"source": "123", "target": "456", "weight": 2}
  ],
  "metadata": {...}
}
```

### 3. Citation Network
- **GET** `/api/citation-network`
- Returns the paper citation network data
- Response format:
```json
{
  "nodes": [
    {"id": "W123", "title": "Paper Title", "year": 2023, "citationCount": 100}
  ],
  "links": [
    {"source": "W123", "target": "W456"}
  ],
  "metadata": {...}
}
```

### 4. Papers List
- **GET** `/api/papers`
- Returns all papers data
- Response format:
```json
{
  "total": 1000,
  "papers": [...]
}
```

### 5. Authors List
- **GET** `/api/authors`
- Returns all authors data
- Response format:
```json
{
  "total": 20819,
  "authors": [...]
}
```

### 6. Statistics
- **GET** `/api/stats`
- Returns network statistics
- Response format:
```json
{
  "author_network": {
    "nodes": 1134,
    "links": 36623,
    "metadata": {...}
  },
  "citation_network": {
    "nodes": 69,
    "links": 14,
    "metadata": {...}
  }
}
```

### 7. Health Check
- **GET** `/health`
- Returns server health status

## Data Processing Details

### Data Source
- **Dataset**: OpenAlex (SciSciNet)
- **Institution**: UC San Diego
- **Field**: Computer Science
- **Time Range**: 2020-2025
- **Total Papers**: 1000 (downloaded)
- **CS Papers**: 69 (filtered)

### Network Statistics

**Author Collaboration Network:**
- Nodes: 1,134 authors
- Links: 36,623 collaborations
- Average collaborations per pair: 1.16
- Most prolific author: 3 papers

**Citation Network:**
- Nodes: 69 papers
- Links: 14 citations (internal)
- Average citations per paper: 645.65
- Most cited paper: 5,934 citations

## Development

### Adding New Endpoints

Edit `app.py` and add new routes:

```python
@app.route('/api/your-endpoint')
def your_function():
    # Your code here
    return jsonify(data)
```

### CORS Configuration

Currently allows all origins. For production, modify in `app.py`:

```python
CORS(app, origins=['http://localhost:3000'])  # Your frontend URL
```

## Testing

```bash
# Test the API
curl http://localhost:5000/
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/author-network
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Data Files Not Found
Make sure you've run the data processing scripts:
```bash
cd scripts
python download_data.py
python build_author_network.py
python build_citation_network.py
```

### Import Errors
Install all dependencies:
```bash
pip install -r requirements.txt
```

## Author

Carol Zhang - UCSD MS in Computer Science

## Assignment

This is Project 1 (Full-Stack Web Development) for the coding test.
- Task 1 (T1): Create interactive node-link graphs
- Task 2 (T2): Create coordinated dashboards
- Task 3 (T3): Refine network with edge bundling