# api_requests.py
import requests
from requests.auth import HTTPBasicAuth

PETFINDER_API_BASE_URL = 'https://api.petfinder.com/v2/'
PETFINDER_API_KEY = 'API KEY'
PETFINDER_API_SECRET = 'API SECRET'

def get_animal_data(pokemon_type_preference):
    type_mapping = {
        'A. Dog': 'dog',
        'B. Scales-Fins-Other': 'scales-fins-other',
        'C. Cat': 'cat',
    }

    animal_type = type_mapping.get(pokemon_type_preference)

    headers = {
        'Authorization': f'Bearer {get_petfinder_access_token()}',
    }

    api_url = f'{PETFINDER_API_BASE_URL}animals?type={animal_type}&limit=1'
    print(f"API URL: {api_url}") 

    response = requests.get(api_url, headers=headers)

    try:
        response.raise_for_status() 
        animal_data = response.json()

        if 'animals' in animal_data and animal_data['animals']:
            matched_animal = animal_data['animals'][0]
            return {
                'name': matched_animal['name'],
                'species': matched_animal['species'],
                'image_url': matched_animal.get('photos', [{}])[0].get('large', ''),
                'description': matched_animal.get('description', ''),
            }
        else:
            return None
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None

def get_petfinder_access_token():
    auth_url = 'https://api.petfinder.com/v2/oauth2/token'
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': PETFINDER_API_KEY,
        'client_secret': PETFINDER_API_SECRET,
    }

    try:
        response = requests.post(auth_url, data=auth_data, auth=HTTPBasicAuth(PETFINDER_API_KEY, PETFINDER_API_SECRET))
        response.raise_for_status()
        access_token = response.json().get('access_token')

        if access_token:
            return access_token
        else:
            print("Error: Unable to obtain Petfinder access token.")
            return None
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None

def get_pokemon_data(pokemon_personality):
    try:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_personality}')
        response.raise_for_status() 
        pokemon_data = response.json()
        return {
            'name': pokemon_data['name'],
            'species': pokemon_data['species']['name'],
            'image_url': pokemon_data['sprites']['front_default'],
        }
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None
