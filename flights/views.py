from django.shortcuts import render, redirect
from django.conf import settings
from amadeus import Client, ResponseError
from .models import Booking
from datetime import datetime

amadeus = Client(
    client_id=settings.AMADEUS_API_KEY,
    client_secret=settings.AMADEUS_API_SECRET,
    hostname='test' 
)

def search_flight(request):
    """Halaman pencarian penerbangan"""
    return render(request, 'flights/search_flight.html')

def flight_results(request):
    """Halaman hasil pencarian penerbangan"""
    if request.method == 'POST':
        departure_city = request.POST.get('departure_city')
        arrival_city = request.POST.get('arrival_city')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date', None)
        is_round_trip = bool(return_date)
        
        try:
            search_params = {
                'originLocationCode': departure_city,
                'destinationLocationCode': arrival_city,
                'departureDate': departure_date,
                'adults': 1,
                'max': 10
            }
            
            if is_round_trip and return_date:
                search_params['returnDate'] = return_date
            
            response = amadeus.shopping.flight_offers_search.get(**search_params)
            
            flights = response.data
            
            request.session['search_params'] = {
                'departure_city': departure_city,
                'arrival_city': arrival_city,
                'departure_date': departure_date,
                'return_date': return_date,
                'is_round_trip': is_round_trip
            }
            
            request.session['flights_data'] = []
            for flight in flights:
                flight_info = {
                    'id': flight['id'],
                    'validating_airline': flight['validatingAirlineCodes'][0] if flight.get('validatingAirlineCodes') else 'N/A',
                    'price': flight['price']['total'],
                    'currency': flight['price']['currency'],
                    'outbound': {
                        'carrier': flight['itineraries'][0]['segments'][0].get('carrierCode', 'N/A'),
                        'number': flight['itineraries'][0]['segments'][0].get('number', 'N/A'),
                        'departure_iata': flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                        'arrival_iata': flight['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                        'departure_time': flight['itineraries'][0]['segments'][0]['departure']['at'],
                        'arrival_time': flight['itineraries'][0]['segments'][0]['arrival']['at'],
                        'duration': flight['itineraries'][0]['duration']
                    }
                }
                
                if len(flight['itineraries']) > 1:
                    flight_info['return'] = {
                        'carrier': flight['itineraries'][1]['segments'][0].get('carrierCode', 'N/A'),
                        'number': flight['itineraries'][1]['segments'][0].get('number', 'N/A'),
                        'departure_iata': flight['itineraries'][1]['segments'][0]['departure']['iataCode'],
                        'arrival_iata': flight['itineraries'][1]['segments'][0]['arrival']['iataCode'],
                        'departure_time': flight['itineraries'][1]['segments'][0]['departure']['at'],
                        'arrival_time': flight['itineraries'][1]['segments'][0]['arrival']['at'],
                        'duration': flight['itineraries'][1]['duration']
                    }
                
                request.session['flights_data'].append(flight_info)
            
            context = {
                'flights': flights,
                'departure_city': departure_city,
                'arrival_city': arrival_city,
                'departure_date': departure_date,
                'return_date': return_date,
                'is_round_trip': is_round_trip
            }
            
            return render(request, 'flights/flight_results.html', context)
            
        except ResponseError as error:
            context = {
                'error': 'Tidak dapat menemukan penerbangan. Silakan coba lagi.',
                'error_detail': str(error)
            }
            return render(request, 'flights/flight_results.html', context)
    
    return redirect('search_flight')

def flight_booking(request, flight_index):
    """Halaman booking penerbangan"""
    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name')
        passport_number = request.POST.get('passport_number')
        

        search_params = request.session.get('search_params', {})
        flights_data = request.session.get('flights_data', [])
        
        if flight_index < len(flights_data):
            selected_flight = flights_data[flight_index]
            
            booking = Booking.objects.create(
                flight_code=f"{selected_flight['validating_airline']}-{selected_flight['outbound']['carrier']}{selected_flight['outbound']['number']}",
                departure_city=search_params.get('departure_city', ''),
                arrival_city=search_params.get('arrival_city', ''),
                departure_date=search_params.get('departure_date', datetime.now().date()),
                return_date=search_params.get('return_date', None) if search_params.get('return_date') else None,
                price=selected_flight['price'],
                passenger_name=passenger_name,
                passport_number=passport_number
            )
            
            context = {
                'booking': booking,
                'is_round_trip': search_params.get('is_round_trip', False),
                'flight_info': selected_flight
            }
            
            return render(request, 'flights/booking_success.html', context)
    
    search_params = request.session.get('search_params', {})
    flights_data = request.session.get('flights_data', [])
    
    selected_flight = None
    if flight_index < len(flights_data):
        selected_flight = flights_data[flight_index]
    
    context = {
        'flight_index': flight_index,
        'search_params': search_params,
        'selected_flight': selected_flight
    }
    
    return render(request, 'flights/flight_booking.html', context)