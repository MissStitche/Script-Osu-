import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# Configurer les variables
API_URL = "https://osu.ppy.sh/api/v2"
CLIENT_SECRET = "Remplacez par votre client secret"
CLIENT_ID = "Remplacez par votre client ID"
USER_ID = "Remplacez par votre user ID"
DOWNLOAD_FOLDER = "./beatmaps"

# Fonction pour se connecter à l'API osu! et récupérer un token d'accès
def get_access_token(api_url, client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.post("https://osu.ppy.sh/oauth/token", data=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Erreur lors de la récupération du token d'accès")
        print(response.json())
        return None

# Fonction pour obtenir les informations des beatmaps
def get_beatmap_info(api_url, user_id, access_token, section, limit=100, offset=0):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit': limit,
        'offset': offset
    }
    response = requests.get(f'{api_url}/users/{user_id}/beatmapsets/{section}', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors du téléchargement des beatmaps de la section {section}")
        print(response.json())
        return []

# Fonction pour télécharger une beatmap
def download_beatmap(beatmapset_id, beatmap_title, download_folder):
    response = requests.get(f"https://beatconnect.io/b/{beatmapset_id}")
    if response.status_code == 200:
        sanitized_title = "".join([c if c.isalnum() else "_" for c in beatmap_title])
        file_path = os.path.join(download_folder, f"{sanitized_title}.osz")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    else:
        print(f"Erreur lors du téléchargement de la beatmap {beatmapset_id}")
        return None
import time 
# Fonction pour ouvrir les fichiers avec l'application par défaut
def open_files_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            try:
                subprocess.Popen(["start", "", file_path], shell=True)
                print(f"Ouverture du fichier {file_name}")
                time.sleep(2)
            except Exception as e:
                print(f"Erreur lors de l'ouverture du fichier {file_name}: {e}")

# Fonction pour obtenir les informations des beatmaps et les télécharger en parallèle
def fetch_and_download_beatmaps(api_url, user_id, access_token, section, download_folder):
    limit = 100
    offset = 0
    has_more = True
    with ThreadPoolExecutor(max_workers=10) as executor:
        download_futures = []

        while has_more:
            beatmaps = get_beatmap_info(api_url, user_id, access_token, section, limit, offset)
            if not beatmaps:
                break

            for beatmap in beatmaps:
                beatmapset_id = beatmap['beatmapset']['id']
                beatmap_title = beatmap['beatmapset']['title']
                download_futures.append(executor.submit(download_beatmap, beatmapset_id, beatmap_title, download_folder))

            if len(beatmaps) < limit:
                has_more = False
            offset += limit

        for future in as_completed(download_futures):
            future.result()

# Obtenir le token d'accès
ACCESS_TOKEN = get_access_token(API_URL, CLIENT_ID, CLIENT_SECRET)

if ACCESS_TOKEN:
    # # Obtenir et télécharger les beatmaps en parallèle
    # fetch_and_download_beatmaps(API_URL, USER_ID, ACCESS_TOKEN, 'most_played', DOWNLOAD_FOLDER)

    # # Ouvrir les fichiers téléchargés (équivalent d'un double-clic)
    open_files_in_folder(DOWNLOAD_FOLDER)

    print("Les beatmaps ont été téléchargées avec succès")
else:
    print("Impossible d'obtenir un jeton d'accès valide")
