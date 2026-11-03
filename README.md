# Smart Campus Lost & Found Matcher

A modern web application built with **Python Flask**, **SQLite**, and **Scikit-learn** designed to help college students and campus administrators efficiently match and recover lost belongings across university grounds.

The system uses Natural Language Processing (NLP) with **TF-IDF vectorization** and **Cosine Similarity** to automatically evaluate descriptions, categories, colours, and locations, calculating a similarity match score between lost and found items in real-time—with zero external AI API costs or third-party dependencies.

---

## 🌟 Key Features

1. **Campus Dashboard & Metrics**:
   - Live counters for Total Reports, Lost Items, Found Items, Active Cases, and Returned Items.
   - Comprehensive directory with search keywords, category filters, type filters (Lost vs. Found), and status filters (Active vs. Returned).

2. **Lost & Found Reporting**:
   - Clean, intuitive reporting forms capturing item name, category, colour, location, detailed description, and contact info / hand-off point.
   - Immediate automatic evaluation against all opposite active reports upon submission.

3. **Smart Matching Engine (TF-IDF & Cosine Similarity)**:
   - Text normalization, token weighting, and stop-words removal powered by Scikit-learn.
   - Feature engineering combining item names, categories, colors, and free-text descriptions.
   - Displays match confidence percentages (0% – 100%) with dynamic visual indicators.

4. **Global Campus Matching Matrix (`/matches`)**:
   - A campus-wide matching overview pairing active lost items with candidate found items side-by-side.

5. **Status Workflow (Active -> Returned)**:
   - One-click status toggling allowing students or campus lost & found desks to mark items as "Returned" once reunited.

6. **Responsive Campus UI**:
   - Styled with modern typography (Plus Jakarta Sans), responsive CSS card grids, clean status badges, and mobile-friendly layouts.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Machine Learning / NLP**: Scikit-Learn (`TfidfVectorizer`, `cosine_similarity`), NumPy
- **Database**: SQLite 3 (lightweight, zero configuration, persistent file)
- **Frontend**: HTML5, CSS3 (Custom Responsive Design System), Vanilla JavaScript
- **Testing**: Pytest, Playwright

---

## 🚀 How to Run the Application Locally

### Prerequisites
- Python 3.10+ installed
- pip (Python package manager)

### 1. Clone & Navigate to Repository
```bash
git clone <repo-url>
cd workshop
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database (Optional, app does this automatically)
The application will automatically initialize `campus_lost_found.db` with sample campus items if it does not already exist:
```bash
python3 database.py
```

### 5. Start the Flask Server
```bash
python3 app.py
```
By default, the server runs on `http://127.0.0.1:5000/`. Open this URL in any browser.

---

## 🧪 Running Automated Tests

Run the full test suite with:
```bash
pytest
```

To run individual test modules:
```bash
pytest tests/test_matcher.py   # Test TF-IDF and similarity algorithm
pytest tests/test_api.py       # Test API endpoints and database operations
pytest tests/test_views.py     # Test Flask web views and template rendering
```

---

## 🧠 Smart Matching Algorithm Details

The matching system in `matcher.py` works as follows:
1. **Attribute Ensembling**: The item's title, category, colour, location, and description are assembled into a composite document. Key attributes (name, category, colour) are emphasized.
2. **Text Preprocessing**: Text is normalized to lowercase and stripped of punctuation while retaining alphanumeric tokens.
3. **TF-IDF Vectorization**: Term Frequency-Inverse Document Frequency matrix is constructed using Scikit-Learn's `TfidfVectorizer` with sublinear TF scaling and standard English stop-words filtering.
4. **Cosine Similarity**: Vector angles between lost reports and found reports are measured using `cosine_similarity(X, Y)`.
5. **Taxonomic Boosting & Thresholding**: Exact category agreements receive a bonus multiplier, producing an intuitive 0% to 100% confidence rating shown in progress bars and badges.

---

## 📂 Project Structure

```
├── app.py                   # Main Flask application and HTTP route handlers
├── database.py              # SQLite schema, connection helpers, and CRUD queries
├── matcher.py               # TF-IDF & Cosine Similarity matching engine
├── requirements.txt         # Project dependencies
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Base navigation, flash alerts, and layout
│   ├── index.html           # Main dashboard and item directory
│   ├── report.html          # Lost and found report submission form
│   ├── item_detail.html     # Item details and ranked smart match suggestions
│   └── matches.html         # Campus-wide matching matrix
├── static/
│   ├── css/style.css        # Responsive CSS styling & campus theme
│   └── js/main.js           # Client-side dynamic features & notifications
└── tests/
    ├── test_matcher.py      # Matching algorithm unit tests
    ├── test_api.py          # REST API & DB update tests
    └── test_views.py        # Web route and rendering tests
```
