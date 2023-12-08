# app.py
import random
import requests
from flask import Flask, render_template, request, redirect, url_for
from api_requests import get_animal_data, get_petfinder_access_token, get_pokemon_data, PETFINDER_API_BASE_URL 



app = Flask(__name__)

quiz_questions = [
    {"id": 1, "question": "How active are you?", "options": ["A. Very Active", "B. Somewhat Active", "C. Not Active"]},
    {"id": 2, "question": "Which size pet do you prefer?", "options": ["A. Large", "B. Small", "C. Medium"]},
    {"id": 4, "question": "What is your preferred habitat?", "options": ["A. Forest", "B. Ocean", "C. Desert"]},
    {"id": 5, "question": "Which weather do you like the most?", "options": ["A. Sunny", "B. Rainy", "C. Stormy"]},
    {"id": 6, "question": "How do you spend your free time?", "options": ["A. Exploring", "B. Relaxing", "C. Training"]},
    {"id": 8, "question": "How would your friends describe you?", "options": ["A. Energetic", "B. Easygoing", "C. Thoughtful"]},
    {"id": 7, "question": "Which Pokémon type do you prefer?", "options": ["A. Fire", "B. Water", "C. Earth"]},
]

quiz_responses = {}

def get_overall_majority_response(quiz_responses):
    response_count = {'A': 0, 'B': 0, 'C': 0}

    for question_id, response in quiz_responses.items():
        option = response.split('.')[0].strip()
        response_count[option] += 1

    return max(response_count, key=response_count.get)

@app.route('/')
def about():
    return render_template('index.html')

@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    global quiz_responses

    if request.method == 'POST':
       
        for question in quiz_questions:
            question_id = question['id']
            selected_option = request.form.get(f'question_{question_id}')
            quiz_responses[f'question_{question_id}'] = selected_option

        return redirect(url_for('results'))

    return render_template('quiz.html', quiz_questions=quiz_questions)

@app.route("/results")
def results():
    global quiz_responses

    matched_animal = assign_animal_by_type(quiz_responses)

    matched_pokemon = assign_pokemon_by_type(quiz_responses)

    return render_template('results.html', matched_animal=matched_animal, matched_pokemon=matched_pokemon)

def assign_pokemon_by_type(quiz_responses):
    overall_majority_response = get_overall_majority_response(quiz_responses)

    if overall_majority_response == 'A':
        return get_random_pokemon_by_type(['fire'])
    elif overall_majority_response == 'B':
        return get_random_pokemon_by_type(['water'])
    elif overall_majority_response == 'C':
        return get_random_pokemon_by_type(['ground'])
    else:
        return None



def get_random_pokemon_by_type(pokemon_types):
    if 'fire' in pokemon_types:
        response = requests.get('https://pokeapi.co/api/v2/type/fire')
        fire_pokemon_data = response.json()['pokemon']
        random_fire_pokemon = random.choice(fire_pokemon_data)['pokemon']['name']
        return get_pokemon_data(random_fire_pokemon)
    elif 'water' in pokemon_types:
        response = requests.get('https://pokeapi.co/api/v2/type/water')
        water_pokemon_data = response.json()['pokemon']
        random_water_pokemon = random.choice(water_pokemon_data)['pokemon']['name']
        return get_pokemon_data(random_water_pokemon)
    elif 'ground' in pokemon_types:
        response = requests.get('https://pokeapi.co/api/v2/type/ground')
        ground_pokemon_data = response.json()['pokemon']
        random_ground_pokemon = random.choice(ground_pokemon_data)['pokemon']['name']
        return get_pokemon_data(random_ground_pokemon)
    else:
        return None


def assign_animal_by_type(quiz_responses):
    overall_majority_response = get_overall_majority_response(quiz_responses)

    if overall_majority_response == 'A':
        return get_random_animal_by_type(['dog'])
    elif overall_majority_response == 'B':
        return get_random_animal_by_type(['scales-fins-other'])
    elif overall_majority_response == 'C':
        return get_random_animal_by_type(['cat'])
    else:
        return None


def get_adoption_info(animal_id):
    headers = {
        'Authorization': f'Bearer {get_petfinder_access_token()}',
    }

    response = requests.get(f'{PETFINDER_API_BASE_URL}animals/{animal_id}', headers=headers)

    try:
        response.raise_for_status()
        animal_info = response.json()

        if 'animal' in animal_info:
            return {
                'url': animal_info['animal'].get('url', ''),
                'contact': animal_info['animal'].get('contact', {}),
            }
        else:
            return {}
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return {}


def get_random_animal_by_type(animal_types):
    if not animal_types:
        return None

    type_param = ','.join(animal_types)

    headers = {
        'Authorization': f'Bearer {get_petfinder_access_token()}',
    }

    response = requests.get(f'{PETFINDER_API_BASE_URL}animals?type={type_param}&limit=5', headers=headers)

    try:
        response.raise_for_status()
        animal_data = response.json()

        # helps filter out animals w no photo
        available_animals = [animal for animal in animal_data.get('animals', []) if animal.get('description') and animal.get('photos')]

        if available_animals:
            matched_animal = random.choice(available_animals)

            adoption_info = get_adoption_info(matched_animal['id'])
            matched_animal_info = {
                'name': matched_animal['name'],
                'species': matched_animal['species'],
                'image_url': matched_animal.get('photos', [{}])[0].get('large', '') if matched_animal.get('photos', []) else '',
                'description': matched_animal.get('description', ''),
                'adoption_info': adoption_info,
            }

            return matched_animal_info
        else:
            return None
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None


if __name__ == '__main__':
    app.run(debug=True)