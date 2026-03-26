#!/usr/bin/env python3
"""
Script to populate the 'country' table from a local JSON file.
"""

import sys
import os

import json
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session


from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from zb_quotes.models.models import Country

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "sqlite:////path/to/your/database.db" defined in .env file
logger.info(f"Using DATABASE_URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL, echo=False)

JSON_FILE = Path("countries/data/countries_fallback_latest.json")  # Path to your JSON file
if not JSON_FILE.exists():
    JSON_FILE = Path("./scripts/countries/data/countries_fallback_latest.json")


def load_json_data(json_path):
    """Load country data from JSON file."""
    logger.info("Loading JSON data from %s", json_path)
    
    if not json_path.exists():
        logger.error("JSON file not found: %s", json_path)
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info("Loaded %d countries from JSON", len(data))
        return data
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format: %s", e)
        return None
    except Exception as e:
        logger.error("Error reading JSON file: %s", e)
        return None


def prepare_country_objects(data):
    """Convert JSON data to list of Country objects."""
    countries = []
    skipped = 0
    
    for entry in data:
        # Extract ISO code (cca2)
        iso_code = entry.get("cca2")
        if not iso_code:
            logger.warning("Skipping entry with missing cca2: %s", entry.get("name", {}).get("common", "unknown"))
            skipped += 1
            continue
        
        # Extract common name
        name = entry.get("name", {}).get("common")
        official_name = entry.get("name", {}).get("official")
        if not name:
            logger.warning("Skipping country with missing common name: %s", iso_code)
            skipped += 1
            continue
        
        # Extract region and subregion
        region = entry.get("region", "")
        subregion = entry.get("subregion", "")
        
        # Create description from region and subregion
        # description = f"{region}, {subregion}".strip(", ") if region or subregion else None
        description = official_name
        
        # Create Country object
        country = Country(
            iso_code_2=iso_code,
            name=name,
            description=description,
            region=region if region else None,
            subregion=subregion if subregion else None
        )
        countries.append(country)
    
    logger.info("Prepared %d country objects (skipped %d)", len(countries), skipped)
    return countries


def save_to_database(session, countries):
    """Save countries to database using merge to avoid duplicates."""
    saved_count = 0
    updated_count = 0
    
    for country in countries:
        # Check if country already exists by iso_code_2
        # result = session.query(Country).filter_by(iso_code_2=country.iso_code_2)
        # existing = result.first()
        stmt = select(Country).where(Country.iso_code_2 == country.iso_code_2)
        existing = session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing record
            existing.name = country.name
            existing.description = country.description
            existing.region = country.region
            existing.subregion = country.subregion
            updated_count += 1
        else:
            # Insert new record
            session.add(country)
            saved_count += 1
    
    session.commit()
    logger.info("Database updated: %d new countries inserted, %d updated", saved_count, updated_count)
    return saved_count, updated_count


def display_sample(session, limit=5):
    """Display sample records from the database."""
    # countries = session.query(Country).limit(limit).all()
    stmt = select(Country).limit(limit)
    countries = session.execute(stmt).scalars().all()
    
    logger.info("\n=== Sample records from database ===")
    for country in countries:
        logger.info("  %s (%s) - %s, %s", 
                   country.name, 
                   country.iso_code_2,
                   country.region or "N/A",
                   country.subregion or "N/A")
    logger.info("===================================\n")


def main():
    # Create database engine and tables
    # engine = create_engine(DATABASE_URL, echo=False)
    # Base.metadata.create_all(engine)
    logger.info("Database tables created/verified")
    
    # Create session
    # Session = sessionmaker(bind=engine)
    # session = Session()
    
    with Session(engine) as session:

        try:
            # Load data from JSON
            raw_data = load_json_data(JSON_FILE)
            if not raw_data:
                logger.error("No data to process. Exiting.")
                return
            
            # Prepare Country objects
            countries = prepare_country_objects(raw_data)
            if not countries:
                logger.warning("No valid country data to insert.")
                return
            
            # Save to database
            saved, updated = save_to_database(session, countries)
            
            # Display sample records
            display_sample(session)
            
            # Summary
            # total_count = session.query(Country).count()
            total_count = session.execute(select(Country)).scalar()
            logger.info("Summary: Total %d countries in database", total_count)
            
        except Exception as e:
            logger.exception("Unexpected error occurred")
            session.rollback()
            raise
        finally:
            session.close()
            logger.info("Database session closed")


if __name__ == "__main__":
    main()