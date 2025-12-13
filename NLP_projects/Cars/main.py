import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import time
from datetime import datetime, timedelta
import logging
from urllib.parse import quote_plus
import sqlite3
import hashlib

def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.fromisoformat(s.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Car:
    name: str
    price: int
    year: int
    mileage: int
    fuel_type: str
    body_type: str
    brand: str
    transmission: str
    location: str
    url: str
    description: str
    image_url: str = ""
    mpg: Optional[float] = None
    safety_rating: Optional[int] = None

class DatabaseManager:
    def __init__(self, db_path: str = "cars_cache.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_hash TEXT UNIQUE,
                data TEXT,
                timestamp DATETIME,
                expiry_date DATETIME
            )
        """)
        conn.commit()
        conn.close()
    
    def get_cached_data(self, search_params: str) -> Optional[List[Car]]:
        search_hash = hashlib.md5(search_params.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data FROM cars_cache 
            WHERE search_hash = ? AND expiry_date > ?
        """, (search_hash, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                data = json.loads(result[0])
                return [Car(**car_data) for car_data in data]
            except:
                return None
        return None
    
    def cache_data(self, search_params: str, cars: List[Car], hours: int = 24):
        search_hash = hashlib.md5(search_params.encode()).hexdigest()
        expiry_date = datetime.now() + timedelta(hours=hours)
        
        cars_data = [car.__dict__ for car in cars]
        data_json = json.dumps(cars_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cars_cache 
            (search_hash, data, timestamp, expiry_date)
            VALUES (?, ?, ?, ?)
        """, (search_hash, data_json, datetime.now(), expiry_date))
        
        conn.commit()
        conn.close()

class CarDataFetcher:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_cars_from_autotrader(self, max_price: int = 50000, location: str = "10001") -> List[Car]:
        cars = []
        try:
            base_url = "https://www.autotrader.com/cars-for-sale/all-cars"
            params = {
                'zip': location,
                'maxPrice': max_price,
                'searchRadius': '100',
                'sortBy': 'relevance',
                'numRecords': '25'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            car_listings = soup.find_all('div', class_='inventory-listing')
            
            for listing in car_listings[:15]:
                try:
                    car = self.parse_autotrader_listing(listing)
                    if car:
                        cars.append(car)
                except Exception as e:
                    logger.warning(f"Error parsing listing: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching from AutoTrader: {e}")
            return self.get_fallback_data(max_price)
        
        return cars if cars else self.get_fallback_data(max_price)
    
    def parse_autotrader_listing(self, listing) -> Optional[Car]:
        try:
            name_elem = listing.find('h2') or listing.find('h3')
            name = name_elem.text.strip() if name_elem else "Unknown Car"
            
            price_elem = listing.find('span', class_='price')
            price_text = price_elem.text.strip() if price_elem else "$0"
            price = int(re.sub(r'[^\d]', '', price_text)) if price_text else 0
            
            year_match = re.search(r'(\d{4})', name)
            year = int(year_match.group(1)) if year_match else 2020
            
            mileage_elem = listing.find('span', string=re.compile(r'miles'))
            mileage = 0
            if mileage_elem:
                mileage_text = mileage_elem.text.strip()
                mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*)', mileage_text)
                mileage = int(mileage_match.group(1).replace(',', '')) if mileage_match else 0
            
            link_elem = listing.find('a', href=True)
            url = f"https://www.autotrader.com{link_elem['href']}" if link_elem else ""
            
            img_elem = listing.find('img')
            image_url = img_elem.get('src', '') if img_elem else ""
            
            brand = self.extract_brand(name)
            fuel_type = self.determine_fuel_type(name)
            body_type = self.determine_body_type(name)
            
            return Car(
                name=name,
                price=price,
                year=year,
                mileage=mileage,
                fuel_type=fuel_type,
                body_type=body_type,
                brand=brand,
                transmission="Automatic",
                location="Various",
                url=url,
                description=f"{year} {name}",
                image_url=image_url
            )
        
        except Exception as e:
            logger.warning(f"Error parsing individual listing: {e}")
            return None
    
    def fetch_cars_from_cargurus(self, max_price: int = 50000) -> List[Car]:
        cars = []
        try:
            base_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action"
            params = {
                'sourceContext': 'cargurusHomePageModel',
                'entitySelectingHelper.selectedEntity': 'c21571',
                'zip': '10001'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error fetching from CarGurus: {e}")
        
        return cars
    
    def get_fallback_data(self, max_price: int) -> List[Car]:
        fallback_cars = [
            Car("2023 Honda Civic", 28500, 2023, 15000, "Gasoline", "Sedan", "Honda", "CVT", "Local Dealer", "#", "Reliable compact sedan", mpg=32.0, safety_rating=5),
            Car("2022 Toyota Camry", 31200, 2022, 22000, "Hybrid", "Sedan", "Toyota", "CVT", "Local Dealer", "#", "Efficient midsize sedan", mpg=28.0, safety_rating=5),
            Car("2023 Tesla Model 3", 42990, 2023, 8000, "Electric", "Sedan", "Tesla", "Single-Speed", "Tesla Store", "#", "Electric luxury sedan", mpg=120.0, safety_rating=5),
            Car("2022 Ford F-150", 38500, 2022, 18000, "Gasoline", "Truck", "Ford", "10-Speed Automatic", "Ford Dealer", "#", "Best-selling pickup truck", mpg=24.0, safety_rating=4),
            Car("2023 Honda CR-V", 33200, 2023, 12000, "Gasoline", "SUV", "Honda", "CVT", "Honda Dealer", "#", "Compact SUV with AWD", mpg=28.0, safety_rating=5),
            Car("2022 Jeep Wrangler", 41800, 2022, 25000, "Gasoline", "SUV", "Jeep", "8-Speed Automatic", "Jeep Dealer", "#", "Off-road capable SUV", mpg=22.0, safety_rating=3),
            Car("2023 BMW 3 Series", 44500, 2023, 9000, "Gasoline", "Sedan", "BMW", "8-Speed Automatic", "BMW Dealer", "#", "Luxury sport sedan", mpg=26.0, safety_rating=5),
            Car("2022 Hyundai Elantra", 24800, 2022, 16000, "Gasoline", "Sedan", "Hyundai", "CVT", "Hyundai Dealer", "#", "Affordable compact sedan", mpg=33.0, safety_rating=4),
            Car("2023 Subaru Outback", 35900, 2023, 11000, "Gasoline", "SUV", "Subaru", "CVT", "Subaru Dealer", "#", "Adventure-ready wagon", mpg=26.0, safety_rating=5),
            Car("2022 Nissan Leaf", 33400, 2022, 14000, "Electric", "Hatchback", "Nissan", "Single-Speed", "Nissan Dealer", "#", "Affordable electric vehicle", mpg=99.0, safety_rating=4)
        ]
        
        return [car for car in fallback_cars if car.price <= max_price]
    
    def extract_brand(self, car_name: str) -> str:
        brands = ['Honda', 'Toyota', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Audi', 'Lexus', 'Acura', 'Infiniti', 'Cadillac', 'Lincoln', 'Buick', 'GMC', 'Jeep', 'Ram', 'Dodge', 'Chrysler', 'Nissan', 'Hyundai', 'Kia', 'Subaru', 'Mazda', 'Volkswagen', 'Volvo', 'Tesla', 'Porsche']
        for brand in brands:
            if brand.lower() in car_name.lower():
                return brand
        return "Unknown"
    
    def determine_fuel_type(self, car_name: str) -> str:
        if any(keyword in car_name.lower() for keyword in ['electric', 'ev', 'tesla', 'leaf', 'bolt']):
            return "Electric"
        elif any(keyword in car_name.lower() for keyword in ['hybrid', 'prius', 'camry hybrid']):
            return "Hybrid"
        else:
            return "Gasoline"
    
    def determine_body_type(self, car_name: str) -> str:
        suv_keywords = ['suv', 'crossover', 'cr-v', 'rav4', 'x3', 'q5', 'escape', 'explorer', 'tahoe', 'suburban', 'pilot', 'highlander', 'pathfinder', 'murano', 'rogue', 'outlander', 'forester', 'outback', 'ascent', 'cx-5', 'cx-9', 'sorento', 'telluride', 'santa fe', 'tucson', 'wrangler', 'grand cherokee', 'compass', 'renegade']
        truck_keywords = ['f-150', 'silverado', '1500', '2500', 'ram', 'tundra', 'tacoma', 'frontier', 'ridgeline', 'ranger', 'colorado', 'canyon']
        hatchback_keywords = ['hatchback', 'hatch', 'golf', 'civic hatchback', 'corolla hatchback', 'leaf', 'bolt']
        
        car_lower = car_name.lower()
        
        if any(keyword in car_lower for keyword in truck_keywords):
            return "Truck"
        elif any(keyword in car_lower for keyword in suv_keywords):
            return "SUV"
        elif any(keyword in car_lower for keyword in hatchback_keywords):
            return "Hatchback"
        else:
            return "Sedan"
    
    def get_cars(self, budget: int, location: str = "10001") -> List[Car]:
        cache_key = f"{budget}_{location}"
        cached_cars = self.db_manager.get_cached_data(cache_key)
        
        if cached_cars:
            logger.info("Using cached car data")
            return cached_cars
        
        logger.info("Fetching fresh car data")
        cars = self.fetch_cars_from_autotrader(budget, location)
        
        if cars:
            self.db_manager.cache_data(cache_key, cars)
        
        return cars

class PreferenceExtractor:
    def __init__(self):
        self.fuel_keywords = {
            'electric': ['electric', 'ev', 'battery', 'zero emission', 'tesla'],
            'hybrid': ['hybrid', 'eco', 'green', 'efficient'],
            'gasoline': ['gas', 'gasoline', 'petrol', 'conventional', 'regular']
        }
        
        self.body_keywords = {
            'sedan': ['sedan', 'car', 'four door', '4 door'],
            'suv': ['suv', 'crossover', 'utility', 'family car'],
            'truck': ['truck', 'pickup', 'hauling'],
            'hatchback': ['hatchback', 'hatch', 'compact']
        }
        
        self.brand_keywords = {
            'honda': ['honda', 'civic', 'accord', 'cr-v'],
            'toyota': ['toyota', 'camry', 'corolla', 'prius', 'rav4'],
            'ford': ['ford', 'f-150', 'escape', 'explorer'],
            'bmw': ['bmw', 'luxury', 'german'],
            'tesla': ['tesla', 'model'],
            'jeep': ['jeep', 'wrangler', 'off-road']
        }
    
    def extract_preferences(self, user_input: str) -> Dict:
        preferences = {
            'budget': None,
            'fuel_type': None,
            'body_type': None,
            'brand_preference': [],
            'priorities': []
        }
        
        user_lower = user_input.lower()
        
        # Budget extraction
        budget_patterns = [
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'budget.*?(\d{1,3}(?:,\d{3})*)',
            r'under.*?(\d{1,3}(?:,\d{3})*)',
            r'around.*?(\d{1,3}(?:,\d{3})*)',
            r'max.*?(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, user_lower)
            if match:
                budget_str = match.group(1).replace(',', '')
                preferences['budget'] = int(budget_str)
                break
        
        # Fuel type
        for fuel_type, keywords in self.fuel_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                preferences['fuel_type'] = fuel_type.title()
                break
        
        # Body type
        for body_type, keywords in self.body_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                preferences['body_type'] = body_type.title()
                break
        
        # Brand preferences
        for brand, keywords in self.brand_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                preferences['brand_preference'].append(brand.title())
        
        # Priorities
        if any(word in user_lower for word in ['reliable', 'reliability']):
            preferences['priorities'].append('reliability')
        if any(word in user_lower for word in ['fuel', 'efficient', 'economy', 'mpg']):
            preferences['priorities'].append('fuel_efficiency')
        if any(word in user_lower for word in ['safe', 'safety']):
            preferences['priorities'].append('safety')
        if any(word in user_lower for word in ['luxury', 'premium', 'high-end']):
            preferences['priorities'].append('luxury')
        if any(word in user_lower for word in ['family', 'kids', 'children']):
            preferences['priorities'].append('family')
        
        return preferences

class RecommendationEngine:
    def __init__(self):
        self.reliability_scores = {
            'honda': 0.95, 'toyota': 0.98, 'lexus': 0.96, 'mazda': 0.88,
            'subaru': 0.85, 'bmw': 0.75, 'mercedes': 0.72, 'audi': 0.74,
            'ford': 0.78, 'chevrolet': 0.76, 'nissan': 0.80, 'hyundai': 0.82,
            'kia': 0.81, 'volkswagen': 0.73, 'jeep': 0.65, 'tesla': 0.70
        }
    
    def calculate_recommendation_score(self, car: Car, preferences: Dict) -> Tuple[float, Dict]:
        scores = {}
        weights = {
            'budget_fit': 0.3,
            'preferences_match': 0.25,
            'reliability': 0.2,
            'efficiency': 0.15,
            'age_mileage': 0.1
        }
        
        # Budget fitness score
        if preferences['budget']:
            if car.price <= preferences['budget']:
                budget_ratio = car.price / preferences['budget']
                scores['budget_fit'] = 1.0 - abs(0.8 - budget_ratio) * 2
            else:
                over_budget = (car.price - preferences['budget']) / preferences['budget']
                scores['budget_fit'] = max(0, 1.0 - over_budget * 2)
        else:
            scores['budget_fit'] = 0.7
        
        scores['budget_fit'] = max(0, min(1, scores['budget_fit']))
        
        # Preferences match
        pref_score = 0.5
        matches = 0
        total_prefs = 0
        
        if preferences['fuel_type']:
            total_prefs += 1
            if car.fuel_type.lower() == preferences['fuel_type'].lower():
                matches += 1
        
        if preferences['body_type']:
            total_prefs += 1
            if car.body_type.lower() == preferences['body_type'].lower():
                matches += 1
        
        if preferences['brand_preference']:
            total_prefs += 1
            if any(brand.lower() == car.brand.lower() for brand in preferences['brand_preference']):
                matches += 1
        
        if total_prefs > 0:
            pref_score = matches / total_prefs
        
        scores['preferences_match'] = pref_score
        
        # Reliability score
        brand_lower = car.brand.lower()
        scores['reliability'] = self.reliability_scores.get(brand_lower, 0.75)
        
        # Efficiency score (MPG or electric equivalent)
        if car.mpg:
            if car.fuel_type.lower() == 'electric':
                scores['efficiency'] = min(1.0, car.mpg / 120.0)
            else:
                scores['efficiency'] = min(1.0, car.mpg / 40.0)
        else:
            scores['efficiency'] = 0.6
        
        # Age and mileage score
        age_score = max(0, 1.0 - (2024 - car.year) / 10.0)
        mileage_score = max(0, 1.0 - car.mileage / 150000)
        scores['age_mileage'] = (age_score + mileage_score) / 2
        
        # Calculate total weighted score
        total_score = sum(scores[key] * weights[key] for key in scores)
        
        return total_score, scores
    
    def generate_explanation(self, car: Car, score: float, score_breakdown: Dict, preferences: Dict) -> str:
        explanation = f"**Why {car.name} is recommended:**\n\n"
        
        if score >= 0.8:
            explanation += "This is an excellent match for your requirements.\n\n"
        elif score >= 0.6:
            explanation += "This is a good match for your requirements.\n\n"
        else:
            explanation += "This car meets some of your requirements.\n\n"
        
        # Budget explanation
        if preferences['budget'] and car.price <= preferences['budget']:
            savings = preferences['budget'] - car.price
            explanation += f"• **Budget-friendly**: Priced at ${car.price:,}, saving you ${savings:,} from your ${preferences['budget']:,} budget.\n"
        elif preferences['budget'] and car.price > preferences['budget']:
            overage = car.price - preferences['budget']
            explanation += f"• **Slight budget stretch**: ${overage:,} over your ${preferences['budget']:,} budget, but offers good value.\n"
        
        # Preference matches
        if preferences['fuel_type'] and car.fuel_type.lower() == preferences['fuel_type'].lower():
            explanation += f"• **Fuel preference match**: {car.fuel_type} engine as requested.\n"
        
        if preferences['body_type'] and car.body_type.lower() == preferences['body_type'].lower():
            explanation += f"• **Body style match**: {car.body_type} configuration as preferred.\n"
        
        if preferences['brand_preference'] and any(brand.lower() == car.brand.lower() for brand in preferences['brand_preference']):
            explanation += f"• **Brand preference**: {car.brand} is one of your preferred brands.\n"
        
        # Reliability
        reliability_score = score_breakdown.get('reliability', 0)
        if reliability_score >= 0.9:
            explanation += f"• **High reliability**: {car.brand} has an excellent reliability record.\n"
        elif reliability_score >= 0.8:
            explanation += f"• **Good reliability**: {car.brand} has a solid reliability reputation.\n"
        
        # Efficiency
        if car.mpg:
            if car.fuel_type.lower() == 'electric':
                explanation += f"• **Efficiency**: {car.mpg} MPGe rating for electric driving.\n"
            else:
                explanation += f"• **Fuel efficiency**: {car.mpg} MPG combined rating.\n"
        
        # Age and condition
        if car.year >= 2022:
            explanation += f"• **Recent model**: {car.year} model year with modern features.\n"
        
        if car.mileage < 30000:
            explanation += f"• **Low mileage**: Only {car.mileage:,} miles on the odometer.\n"
        
        explanation += f"\n**Overall match score: {score*100:.0f}%**"
        
        return explanation
    
    def get_recommendations(self, cars: List[Car], preferences: Dict, top_n: int = 5) -> List[Tuple[Car, float, str]]:
        recommendations = []
        
        for car in cars:
            score, score_breakdown = self.calculate_recommendation_score(car, preferences)
            explanation = self.generate_explanation(car, score, score_breakdown, preferences)
            recommendations.append((car, score, explanation))
        
        # Sort by score in descending order
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:top_n]

def main():
    st.set_page_config(
        page_title="AI Car Recommendation System",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("AI Car Recommendation System")
    st.markdown("Get personalized car recommendations based on your preferences and budget using advanced AI analysis.")
    
    # Initialize components
    if 'fetcher' not in st.session_state:
        st.session_state.fetcher = CarDataFetcher()
    if 'extractor' not in st.session_state:
        st.session_state.extractor = PreferenceExtractor()
    if 'engine' not in st.session_state:
        st.session_state.engine = RecommendationEngine()
    
    # User input section
    st.header("Tell us what you're looking for")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_area(
            "Describe your ideal car",
            placeholder="I'm looking for a reliable family sedan under $35,000 with good fuel economy...",
            height=100
        )
    
    with col2:
        location = st.text_input("Your ZIP Code", value="10001", help="Used for local inventory search")
        max_budget = st.number_input("Maximum Budget ($)", min_value=5000, max_value=200000, value=50000, step=1000)
    
    if st.button("Get Recommendations", type="primary"):
        if user_input.strip():
            with st.spinner("Analyzing your preferences and fetching car data..."):
                # Extract preferences
                preferences = st.session_state.extractor.extract_preferences(user_input)
                if not preferences['budget'] and max_budget:
                    preferences['budget'] = max_budget
                
                # Fetch car data
                cars = st.session_state.fetcher.get_cars(preferences['budget'] or max_budget, location)
                
                if not cars:
                    st.error("Unable to fetch car data. Please try again later.")
                    return
                
                # Get recommendations
                recommendations = st.session_state.engine.get_recommendations(cars, preferences)
                
                # Display results
                st.header("Your Personalized Recommendations")
                
                # Show extracted preferences
                with st.expander("Detected Preferences"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if preferences['budget']:
                            st.write(f"**Budget:** ${preferences['budget']:,}")
                        if preferences['fuel_type']:
                            st.write(f"**Fuel Type:** {preferences['fuel_type']}")
                        if preferences['body_type']:
                            st.write(f"**Body Type:** {preferences['body_type']}")
                    with col2:
                        if preferences['brand_preference']:
                            st.write(f"**Preferred Brands:** {', '.join(preferences['brand_preference'])}")
                        if preferences['priorities']:
                            st.write(f"**Priorities:** {', '.join(preferences['priorities'])}")
                
                # Display recommendations
                for i, (car, score, explanation) in enumerate(recommendations, 1):
                    with st.container():
                        st.subheader(f"#{i}. {car.name}")
                        
                        col1, col2, col3 = st.columns([2, 1, 2])
                        
                        with col1:
                            st.write(f"**Price:** ${car.price:,}")
                            st.write(f"**Year:** {car.year}")
                            st.write(f"**Mileage:** {car.mileage:,} miles")
                            st.write(f"**Fuel Type:** {car.fuel_type}")
                            if car.mpg:
                                mpg_label = "MPGe" if car.fuel_type.lower() == 'electric' else "MPG"
                                st.write(f"**Efficiency:** {car.mpg} {mpg_label}")
                        
                        with col2:
                            st.write(f"**Brand:** {car.brand}")
                            st.write(f"**Body Type:** {car.body_type}")
                            st.write(f"**Transmission:** {car.transmission}")
                            
                            # Match score visualization
                            score_percent = int(score * 100)
                            if score_percent >= 80:
                                score_color = "green"
                            elif score_percent >= 60:
                                score_color = "orange"
                            else:
                                score_color = "red"
                            
                            st.markdown(f"**Match Score:** <span style='color: {score_color}'>{score_percent}%</span>", unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(explanation)
                        
                        if car.url and car.url != "#":
                            st.link_button("View Details", car.url, type="secondary")
                        
                        st.divider()
        else:
            st.warning("Please describe what kind of car you're looking for.")

if __name__ == "__main__":
    main()