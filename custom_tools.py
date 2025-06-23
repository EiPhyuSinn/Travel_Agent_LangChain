from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv
import os 

load_dotenv()
api_key = os.getenv("GEOAPIFY_API_KEY") 

class AviationstackFlightSearchInput(BaseModel):
    flight_number: Optional[str] = Field(None, description="Flight number to search for")
    departure_airport: Optional[str] = Field(None, description="IATA code of departure airport")
    arrival_airport: Optional[str] = Field(None, description="IATA code of arrival airport")
    flight_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    flight_status: Optional[str] = Field(None, description="Flight status: scheduled, active, landed, cancelled, incident, diverted")

class AviationstackTool(BaseTool):
    name: str = "aviationstack_flight_search" 
    description: str = "Search for flight information including status, delays, and schedules"  
    args_schema: Type[BaseModel] = AviationstackFlightSearchInput
    
    def _run(
        self,
        flight_number: Optional[str] = None,
        departure_airport: Optional[str] = None, 
        arrival_airport: Optional[str] = None,
        flight_date: Optional[str] = None,
        flight_status: Optional[str] = None
    ):
        """Search for flights using Aviationstack API"""
        
        params = {
            'access_key': api_key,
            'limit': 5
        }
        
        if flight_number:
            params['flight_number'] = flight_number
        if departure_airport:
            params['dep_iata'] = departure_airport
        if arrival_airport:
            params['arr_iata'] = arrival_airport
        if flight_date:
            params['flight_date'] = flight_date
        if flight_status:
            params['flight_status'] = flight_status
            
        try:
            response = requests.get('https://api.aviationstack.com/v1/flights', params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return "No flight information found for the given parameters."
                
            # Format the response
            formatted_flights = []
            for flight in data['data']:
                flight_info = {
                    'airline': flight['airline']['name'],
                    'flight_number': flight['flight']['iata'],
                    'departure': {
                        'airport': flight['departure']['airport'],
                        'iata': flight['departure']['iata'],
                        'scheduled': flight['departure']['scheduled'],
                        'estimated': flight['departure']['estimated'],
                        'delay': flight['departure']['delay']
                    },
                    'arrival': {
                        'airport': flight['arrival']['airport'],
                        'iata': flight['arrival']['iata'],
                        'scheduled': flight['arrival']['scheduled'],
                        'estimated': flight['arrival']['estimated'],
                        'delay': flight['arrival']['delay']
                    },
                    'status': flight['flight_status']
                }
                formatted_flights.append(flight_info)
                
            return formatted_flights
            
        except Exception as e:
            return f"Error fetching flight data: {str(e)}"

class AviationstackAirportSearchInput(BaseModel):
    search_term: str = Field(description="Airport name or code to search for")

class AviationstackAirportTool(BaseTool):
    name: str = "aviationstack_airport_search"  # ✅ Added type annotations
    description: str = "Search for airport information including IATA/ICAO codes and locations"  # ✅
    args_schema: Type[BaseModel] = AviationstackAirportSearchInput

    def _run(self, search_term: str):
        """Search for airports using Aviationstack API"""
        params = {
            'access_key': api_key,
            'search': search_term,
            'limit': 5
        }

        try:
            response = requests.get('https://api.aviationstack.com/v1/airports', params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get('data'):
                return "No airport information found for the given search term."

            formatted_airports = []
            for airport in data['data']:
                airport_info = {
                    'name': airport.get('airport_name'),
                    'iata': airport.get('iata_code'),
                    'icao': airport.get('icao_code'),
                    'location': {
                        'city': airport.get('city_iata_code', 'Unknown'),
                        'country': airport.get('country_name', 'Unknown'),
                        'timezone': airport.get('timezone', 'Unknown')
                    }
                }
                formatted_airports.append(airport_info)

            return formatted_airports

        except Exception as e:
            return f"Error fetching airport data: {str(e)}"
