import dotenv
import requests
from requests import RequestException
from time import sleep

trakt_url = "https://api.trakt.tv"

trakt_api_key = dotenv.get_key(".env", "TRAKT_API_KEY") # If you are trying to run this you need a Trakt API key

headers = {
    "Content-Type": "application/json",
    "trakt-api-key": trakt_api_key,
    "trakt-api-version": "2",
}


def request_shows(pages: int = 1, limit: int = 10, extended_level: str = ""):
    shows = []

    trakt_shows_url = trakt_url + "/shows/trending"

    for page in range(1, pages + 1):

        params = {
            "page": page,
            "limit": limit,
            "extended": extended_level
        }

        try:
            response = requests.get(trakt_shows_url, params=params, headers=headers)
        except RequestException as e:
            print(e)
            exit(1)

        response.raise_for_status()

        if response.status_code == 429:
            print("Rate limited")
            sleep(int(response.json()["Retry-After"]))

        # print(response.json()[0])

        language_map = {"en": "English", "de": "Deutsch", "ka": "Korean"}

        shows.extend(
            [
                {
                    "title": item["show"]["title"],
                    "type": "",
                    "language": language_map.get(item["show"]["language"]),
                    "genres": item["show"]["genres"],
                    "summary": item["show"].get("overview", "")
                 } for item in response.json()
            ]
        )

    return shows


def request_search(query: str, media_type: str):

    tv_maze_search_url = tv_maze_url + f"/singlesearch/{media_type}"

    params = {
        "q": query,
    }

    try:
        response = requests.get(tv_maze_search_url, params=params, headers=headers)
    except RequestException as e:
        print(e)
        exit(1)

    response.raise_for_status()

    # if response.status_code == 429:
    #     print("Rate limited")
    #     sleep(int(response.json()["Retry-After"]))

    # print(response.json())

    media = {
        "title": response.json()["name"],
        "type": response.json()["type"],
        "language": response.json()["language"],
        "genres": response.json()["genres"],
        "summary": response.json()["summary"].replace("<p>", "").replace("</p>", "")
    }

    return media


if __name__ == "__main__":
    # shows = asyncio.run(request_shows(extended_level="full"))

    # shows = request_shows(10, 10, "full")

    shows = request_search("is it wrong to pick up girls in a dungeon", "shows")

    print(shows)
