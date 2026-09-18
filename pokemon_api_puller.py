"""
Stage 0 Project — API Puller

Pulls Pokemon data from the free PokeAPI (https://pokeapi.co/) — no API key needed.
This script demonstrates the core Stage 0 concepts:
  - Pagination (following "next page" links)
  - Rate limiting (being polite with delays between requests)
  - Retries with backoff (handling flaky network calls)
  - Error handling (not crashing on a bad request)
  - Saving to both CSV and Parquet

Run it with:  python pokemon_api_puller.py
"""

import time
import requests
import pandas as pd
from requests.exceptions import RequestException

BASE_URL = "https://pokeapi.co/api/v2/pokemon"
PAGE_SIZE = 50        # how many records to request per page
MAX_RETRIES = 3        # how many times to retry a failed request
RETRY_DELAY = 2        # seconds to wait before retrying (grows with each attempt)
REQUEST_DELAY = 0.5    # seconds to wait between requests, to be polite to the API


def fetch_with_retries(url, params=None):
    """
    Fetch a URL, retrying on failure. This is the pattern you'll reuse
    constantly in real pipelines — networks and APIs are unreliable,
    so code that assumes every request succeeds will break in production.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # turns a 404/500 into an exception
            return response.json()
        except RequestException as e:
            print(f"  Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)  # wait a bit longer each retry
            else:
                print("  Max retries reached — skipping this request.")
                return None


def fetch_all_pokemon(limit=100):
    """
    Pull the basic list of Pokemon, following pagination until we hit `limit`.
    """
    results = []                                   # empty list — will fill up as we collect pokemon across pages
    url = BASE_URL                                 # start at the first page (the base API address)
    params = {"limit": PAGE_SIZE, "offset": 0}     # tell the API: give me 50 results, starting from position 0

    while url and len(results) < limit:            # keep looping while there's a next page AND we still need more
        data = fetch_with_retries(url, params=params)   # actually fetch this page (with retry logic built in)

        if data is None:                           # if the fetch totally failed even after retries...
            break                                   # ...stop the loop early, no point continuing

        results.extend(data["results"])             # pull the "results" list out of the response, add all of it to our running list
        print(f"Pulled {len(results)} pokemon so far...")  # progress update — shows the running total in the terminal

        url = data.get("next")                      # grab the next page's URL from the response (None if there isn't one)
        params = None                                # clear params — the "next" URL already has them baked in
        time.sleep(REQUEST_DELAY)                    # pause briefly before the next request, to be polite to the API

    return results[:limit]                          # hand back the collected list, trimmed to exactly `limit` items


def fetch_pokemon_details(name_url_pairs):
    """
    For each pokemon in our list, fetch a bit more detail.
    """
    detailed = []                                    # empty list — will hold the enriched pokemon data

    for i, item in enumerate(name_url_pairs):         # loop through the list; `i` = position number, `item` = the entry itself
        data = fetch_with_retries(item["url"])        # fetch this specific pokemon's own detail page

        if data is None:                              # if this one request failed even after retries...
            continue                                   # ...skip just this pokemon, move on to the next one in the loop

        detailed.append({                              # build a small dictionary with just the fields we care about
            "name": data.get("name"),                  # pokemon's name
            "id": data.get("id"),                       # pokemon's numeric ID
            "height": data.get("height"),                # height value from the API
            "weight": data.get("weight"),                # weight value from the API
            "base_experience": data.get("base_experience"),  # base experience value from the API
        })                                                # ...and add that dictionary onto our `detailed` list

        if (i + 1) % 10 == 0:                            # every 10th pokemon (i+1 divisible by 10, no remainder)...
            print(f"Fetched details for {i + 1}/{len(name_url_pairs)} pokemon")  # ...print a progress update

        time.sleep(REQUEST_DELAY)                        # pause briefly before the next request

    return detailed                                      # hand back the full list of detailed pokemon dictionaries


def main():
    print("Starting pull...")                            # first message printed when the script starts running

    basic_list = fetch_all_pokemon(limit=100)             # step 1: get the basic list of 100 pokemon references
    print(f"Got {len(basic_list)} pokemon references. Fetching details...\n")  # confirm how many we got

    detailed = fetch_pokemon_details(basic_list)          # step 2: get full details for each pokemon in that list
    df = pd.DataFrame(detailed)                           # step 3: turn the list of dictionaries into a proper table

    print("\nPreview of your data:")                      # label before showing a sample
    print(df.head())                                      # show just the first 5 rows, as a sanity check

    df.to_csv("pokemon_data.csv", index=False)            # save the table as a CSV file (index=False = no extra row-number column)
    df.to_parquet("pokemon_data.parquet", index=False)    # also save it as a Parquet file, the columnar format

    print(f"\nSaved {len(df)} records to pokemon_data.csv and pokemon_data.parquet")  # final confirmation message


if __name__ == "__main__":       # this is True only when you run the file directly (not when it's imported elsewhere)
    main()                        # ...and if so, actually kick off the whole script by calling main()