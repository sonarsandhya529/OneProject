# Crop Recommendation System (Marathi + English)

A Streamlit project with bilingual UI, farmer registration/login, soil-type guidance, and a machine-learning crop recommendation model.

## Features
- English / Marathi language selector in the sidebar
- Home, farmer registration, farmer login, and dashboard pages
- Farmer accounts include a Maharashtra district selected during registration; dashboard displays the farmer's district
- Farmer accounts stored in a local SQLite database; passwords are salted and hashed
- Optional browser-based geolocation button (requires user permission and a secure context such as localhost/HTTPS)
- Manual district selection during registration; dashboard displays the registered district
- Soil type selection: black, red, alluvial, sandy, clay
- Water availability and season inputs
- ML crop prediction based on N, P, K, temperature, humidity, pH, and rainfall
- Alternative crop labels from the trained model

## Dataset required
Download a crop recommendation CSV dataset with these exact columns:
`N, P, K, temperature, humidity, ph, rainfall, label`

Save it as `Crop_recommendation.csv` in the same folder as `app.py`. Dataset is not included in this ZIP.

## Run on Windows
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Then open `http://localhost:8501`.

## Important
- Soil-type crop lists are general examples, not guaranteed recommendations.
- The ML prediction is only as good as its dataset and does not replace a soil test or local agronomist.
- SQLite storage on free cloud hosting may not be persistent. For real deployments, use a managed database and secure authentication.
- Do not commit farmer records, database files, or secrets to a public repository.


## GPS notes
The dashboard includes an optional browser geolocation button. The user must explicitly grant location permission. Browser geolocation works on localhost and HTTPS deployments in supported browsers; it may not work on plain HTTP or some desktop devices. This version displays latitude/longitude in the embedded panel, but does not automatically reverse-geocode coordinates into a district or change crop predictions based on GPS. The registered district remains manually selected.


### GPS district detection
The dashboard can request browser location, then use OpenStreetMap Nominatim reverse geocoding to estimate the district and show broad district-level crop examples. Internet access is required for reverse geocoding; location permission is required, and hosted deployments generally need HTTPS. The result may be approximate and should be verified. This demo's regional crop lists are illustrative, not an official agricultural advisory.


## Included dataset
This project includes `Crop_recommendation.csv` with 100 demonstration rows across 10 crop labels.
The rows are generated sample values for testing the app workflow, not a verified agricultural dataset.
For real farm decisions, replace it with a validated dataset and follow local soil-test/agricultural advice.
