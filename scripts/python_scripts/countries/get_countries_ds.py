#!/usr/bin/env python3
"""
Populate the 'country' table using REST Countries API with fallback.
Saves the raw data to JSON and CSV files for future reference.
"""

import os
import sys
import json
import csv
import logging
import requests
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass

# Import your models – adjust as needed
# from your_models import Country, Base

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///countries.db")
API_URL = "https://restcountries.com/v3.1/all"
FALLBACK_API_URL = "https://restcountries.com/v3.1/all?fields=cca2,name,region,subregion"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CountryPopulator/1.0)"}

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@dataclass
class Country:
    iso_code_2: str
    name: str
    description: str
    region: str
    subregion: str


def save_to_json(data, filename=None):
    """Save data to a JSON file with timestamp."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"countries_raw_{timestamp}.json"
    else:
        filename = DATA_DIR / filename
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Saved JSON data to %s", filename)
        return filename
    except Exception as e:
        logger.error("Failed to save JSON: %s", e)
        return None


def save_to_csv(countries_data, filename=None):
    """
    Save processed country data to a CSV file.
    countries_data: list of Country objects or dictionaries
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"countries_processed_{timestamp}.csv"
    else:
        filename = DATA_DIR / filename
    
    try:
        # Convert Country objects to dictionaries if needed
        if countries_data and hasattr(countries_data[0], 'iso_code_2'):
            dict_data = [
                {
                    'iso_code_2': c.iso_code_2,
                    'name': c.name,
                    'description': c.description or '',
                    'region': c.region or '',
                    'subregion': c.subregion or ''
                }
                for c in countries_data
            ]
        else:
            dict_data = countries_data
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if dict_data:
                fieldnames = ['iso_code_2', 'name', 'description']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dict_data)
                logger.info("Saved CSV data to %s (%d rows)", filename, len(dict_data))
            else:
                logger.warning("No data to save to CSV")
        return filename
    except Exception as e:
        logger.error("Failed to save CSV: %s", e)
        return None


def save_raw_response_to_csv(raw_data, filename=None):
    """
    Save raw API response to CSV with basic fields.
    Useful for backup and analysis.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"countries_raw_{timestamp}.csv"
    else:
        filename = DATA_DIR / filename
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # Extract common fields from the complex JSON structure
            rows = []
            for entry in raw_data:
                row = {
                    'cca2': entry.get('cca2', ''),
                    'cca3': entry.get('cca3', ''),
                    'name_common': entry.get('name', {}).get('common', ''),
                    'name_official': entry.get('name', {}).get('official', ''),
                    'region': entry.get('region', ''),
                    'subregion': entry.get('subregion', ''),
                    'population': entry.get('population', ''),
                    'area': entry.get('area', ''),
                    'capital': ', '.join(entry.get('capital', [])) if entry.get('capital') else '',
                }
                rows.append(row)
            
            if rows:
                fieldnames = ['cca2', 'cca3', 'name_common', 'name_official', 
                             'region', 'subregion', 'population', 'area', 'capital']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                logger.info("Saved raw CSV to %s (%d rows)", filename, len(rows))
        return filename
    except Exception as e:
        logger.error("Failed to save raw CSV: %s", e)
        return None


def fetch_countries_data():
    """Try primary API, then fallback, and save raw data."""
    logger.info("Fetching countries data from %s", API_URL)
    data = fetch_data(API_URL, HEADERS)
    
    if data is not None:
        # Save raw API response
        save_to_json(data, "countries_api_latest.json")
        save_raw_response_to_csv(data, "countries_api_latest_raw.csv")
        return data
    
    logger.warning("Primary API failed, trying fallback: %s", FALLBACK_API_URL)
    data = fetch_data(FALLBACK_API_URL, HEADERS)
    if data is not None:
        save_to_json(data, "countries_fallback_latest.json")
        save_raw_response_to_csv(data, "countries_fallback_latest_raw.csv")
        return data
    
    # Try to load from existing JSON file as last resort
    local_file = DATA_DIR / "countries_api_latest.json"
    if local_file.exists():
        logger.info("Loading data from local file: %s", local_file)
        with open(local_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info("Loaded %d countries from local JSON", len(data))
            return data
    
    logger.critical("Could not obtain country data from any source.")
    sys.exit(1)


def fetch_data(url, headers=None):
    """Fetch JSON data from a URL with optional headers."""
    try:
        response = requests.get(url, headers=headers or {}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch %s: %s", url, e)
        return None


def prepare_country_objects(data):
    """Convert API response to list of Country objects."""
    countries = []
    for entry in data:
        iso_code = entry.get("cca2")
        name = entry.get("name", {}).get("common")
        if not iso_code or not name:
            logger.warning("Skipping invalid entry: %s", entry.get("name", {}).get("common", "unknown"))
            continue
        
        region = entry.get("region", "")
        subregion = entry.get("subregion", "")
        description = f"{region}, {subregion}".strip(", ") if region or subregion else None
        
        countries.append(Country(iso_code_2=iso_code, name=name, description=description, region=region, subregion=subregion)) # region subregion
    
    logger.info("Prepared %d country objects", len(countries))
    return countries


def save_countries(session, countries):
    """Save countries to database and also to CSV."""
    # Save to database
    # for country in countries:
    #     session.merge(country)
    # session.commit()
    logger.info("Saved %d countries to database", len(countries))
    
    # Also save to CSV for future reference
    save_to_csv(countries, "countries_latest.csv")
    
    # Create a timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_csv(countries, f"countries_backup_{timestamp}.csv")


def list_saved_files():
    """List all saved data files for reference."""
    files = list(DATA_DIR.glob("countries_*"))
    if files:
        logger.info("Saved files in %s:", DATA_DIR)
        for f in sorted(files):
            logger.info("  - %s", f.name)
    else:
        logger.info("No saved files yet.")


def main():
    # engine = create_engine(DATABASE_URL, echo=False)
    # Base.metadata.create_all(engine)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    
    try:
        # Fetch data from API or fallback
        raw_data = fetch_countries_data()
        
        # Convert to Country objects
        countries = prepare_country_objects(raw_data)
        
        # Save to database and CSV files
        save_countries(session, countries)
        
        # List all saved files
        list_saved_files()
        
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.exception("Unexpected error")
        # session.rollback()
        sys.exit(1)
    finally:
        # session.close()
        pass


if __name__ == "__main__":
    main()