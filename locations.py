import requests
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from flask import Flask, render_template, request

app = Flask(__name__)

def get_followers(username: str, bearer_token: str) -> dict:
    """
    Return user's followers' locations after sendind the request.
    """
    base_url = "https://api.twitter.com/"
    search_url = f'{base_url}1.1/friends/list.json'
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    params = {
        'screen_name': username,
        'count':  10
    }
    result = requests.get(search_url, headers = headers, params = params)
    return result.json()

def iteration(username, bearer_token):
    '''
    Return list of users names and coordinates.
    '''
    result_lst = []
    json_dict = get_followers(username, bearer_token)
    for element in json_dict['users']:
        user_screen_name = element["screen_name"]
        user_location = element["location"]
        try:
            geolocator = Nominatim(user_agent='name').geocode(user_location)
            user_coordinates = tuple(geolocator.latitude, geolocator.longitude)
        except GeocoderUnavailable:
            pass
        result_lst.append((user_screen_name, user_coordinates))
    return result_lst

def create_map(username, bearer_token):
    '''
    Create the map.
    '''
    list_of_users = iteration(username, bearer_token)
    my_map = folium.Map()

    map_layer = folium.FeatureGroup(name = "My_map")
    for user, coordinates in list_of_users:
        map_layer.add_child(folium.Marker(location=coordinates, popup=user, icon= folium.Icon()))

    my_map.add_child(map_layer)
    my_map.save('my_map.html')



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods = ['POST'])


def register():
    if not request.form.get('name') or not request.form.get('token'):
        return render_template('failure.html')
    create_map(request.form.get('name'), request.form.get('token'))
    return render_template('my_map.html')

if __name__ == '__main__':
    app.run(debug = False)