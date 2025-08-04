import requests
import datetime
import pytz

LOCAL_TZ = datetime.datetime.now().astimezone().tzinfo

def get_current_airing_anime():
    query = '''
    query ($page: Int, $perPage: Int, $season: MediaSeason, $seasonYear: Int, $status: MediaStatus) {
      Page(page: $page, perPage: $perPage) {
        media(season: $season, seasonYear: $seasonYear, status: $status, type: ANIME, format_in: [TV, TV_SHORT, ONA, OVA]) {
          title {
            romaji
            english
            native
          }
          synonyms
          nextAiringEpisode {
            airingAt
            episode
          }
          coverImage {
            large
          }
          format
        }
      }
    }
    '''

    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if month in [12, 1, 2]:
        season = "WINTER"
    elif month in [3, 4, 5]:
        season = "SPRING"
    elif month in [6, 7, 8]:
        season = "SUMMER"
    else:
        season = "FALL"

    variables = {
        "page": 1,
        "perPage": 100,
        "season": season,
        "seasonYear": year,
        "status": "RELEASING"
    }

    url = "https://graphql.anilist.co"
    response = requests.post(url, json={"query": query, "variables": variables})
    data = response.json()

    anime_list = []
    for anime in data['data']['Page']['media']:
        titles = anime['title']
        synonyms = anime.get('synonyms', [])
        next_ep = anime.get('nextAiringEpisode')

        if next_ep:
            airing_utc = datetime.datetime.fromtimestamp(next_ep['airingAt'], tz=datetime.timezone.utc)
            airing_local = airing_utc.astimezone(LOCAL_TZ)
            weekday = airing_local.strftime('%A')
            time_remaining = airing_local - datetime.datetime.now().astimezone()

            anime_list.append({
                "title": titles['english'] or titles['romaji'],
                "title_romaji": titles['romaji'],
                "title_english": titles['english'],
                "title_native": titles['native'],
                "synonyms": synonyms,
                "episode": next_ep['episode'] - 1,
                "time_remaining": str(time_remaining).split('.')[0],
                "airing_time": airing_local.strftime('%Y-%m-%d %H:%M:%S'),
                "weekday": weekday,
                "format": anime['format'],
                "image_url": anime['coverImage']['large'],
                "airing_at": airing_local
            })

    anime_list.sort(key=lambda x: x['airing_at'])
    return anime_list