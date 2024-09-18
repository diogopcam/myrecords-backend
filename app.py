import json
from flask import Flask, request, jsonify
import requests
import base64
import os
from dotenv import load_dotenv
from requests import post, get
from flask_cors import CORS

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = Flask(__name__)
CORS(app)  # Permite todas as origens


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result["access_token"]
    print(f"Generated Token: {token}")  # Print the token
    return token


def search_for_album_covers(token, query):
    url = f"https://api.spotify.com/v1/search?q={query}&type=album"
    headers = {"Authorization": "Bearer " + token}

    result = get(url, headers=headers)
    json_result = result.json()
    print(f"API Response: {json_result}")  # Print the API response

    # Extrair capas de álbuns dos resultados
    album_data_list = []
    for album in json_result.get('albums', {}).get('items', []):
        album_cover_url = album.get('images', [{}])[0].get('url', None)
        album_data = {
            'albumType': album.get('album_type', 'Unknown'),
            'albumName': album.get('name', 'Unknown'),
            'releaseDate': album.get('release_date', 'Unknown'),
            'albumUri': album.get('external_urls', {}).get('spotify', 'Unknown'),
            'artistName': album['artists'][0].get('name', 'Unknown') if album.get('artists') else 'Unknown',
            'albumCover': album_cover_url
        }
        album_data_list.append(album_data)

    print(f"Album Data: {album_data_list}")  # Print the list of album data
    return album_data_list


@app.route('/api/get_album_covers', methods=['GET'])
def get_album_covers():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    token = get_token()
    album_covers = search_for_album_covers(token, query)
    print(f"Query: {query}")  # Print the query
    print(f"Album Covers Sent to Frontend: {album_covers}")  # Print the album covers sent to frontend
    return jsonify(album_covers)


if __name__ == '__main__':
    app.run(debug=True)