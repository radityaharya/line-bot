import requests
from os import environ
from dotenv import load_dotenv

load_dotenv(override=True)

def tmdb_show_data(tmdb_id, api_key=environ.get("TMDB_API_KEY")):
    if not api_key:
        return {"success": False, "message": "No API key provided"}
    r = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}")
    data = r.json()
    return data

def tmdb_episode_data(tmdb_id, season, episode, api_key=environ.get("TMDB_API_KEY")):
    if api_key is None:
        return {"success": False, "message": "No API key provided"}
    r = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season}/episode/{episode}?api_key={api_key}")
    data = r.json()
    return data

def tmdb_images(tmdb_id, season=None, episode=None):
    if season and episode:
        episode_data = tmdb_episode_data(tmdb_id, season, episode)
        if "success" in episode_data:
            if episode_data["success"] == False:
                path = tmdb_show_data(tmdb_id)["backdrop_path"]
        else:
            path = episode_data['still_path']
            if not path:
                show_data = tmdb_show_data(tmdb_id)
                path = show_data['backdrop_path']
    if path:
        return f"https://image.tmdb.org/t/p/original{path}"
    else:
        return None