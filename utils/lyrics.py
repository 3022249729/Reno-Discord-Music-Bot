from bs4 import BeautifulSoup
import requests
import re
from os import environ as env

GENIUS_TOKEN = env.get("GENIUS_ACCESS_TOKEN")

def search_song_genius(song_title):
    search_url = "https://api.genius.com/search"
    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}"
    }
    params = {
        "q": song_title
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    json_data = response.json()
    
    if json_data['response']['hits']:
        song_data = json_data['response']['hits'][0]['result']
        return song_data
    else:
        return None
    
    
def get_lyrics_text_genius(lyrics_divs):
    lyrics = ""

    for div in lyrics_divs:
        if div is None:
            continue
        
        div_str = str(div)
        div_str = div_str.replace("<br/>", "\n").replace("<br>", "\n")

        soup = BeautifulSoup(div_str, 'html.parser')

        text = soup.get_text()
        
        if re.match(r'\[.*\]', text):
            lyrics += '\n' + text
        else:
            if '<i>' in div_str or '<b>' in div_str:
                lyrics += text
            else:
                lyrics += '\n' + text
    
    return lyrics

def get_lyrics_genius(keyword):
    song_data = search_song_genius(keyword)

    if not song_data:
        return None

    try:
        song_url = f"https://genius.com{song_data['path']}"
        with requests.Session() as session:
            page = session.get(song_url)
            html = BeautifulSoup(page.text, 'html.parser')
    except:
        return None
    
    lyrics_divs = html.find_all('div', {'data-lyrics-container': 'true'})
    lyrics = get_lyrics_text_genius(lyrics_divs)

    return song_data, lyrics

