import requests
import pandas as pd


stats_nba_com_headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}


# Extract the JSON data from HTTP response from stats.nba.com
def extract_data(url, headers=None):
    # Initialize headers if none given
    if headers is None:
        headers = stats_nba_com_headers

    # Send request and get response
    response = requests.get(url, headers=stats_nba_com_headers)
    response = response.json()

    # Get headers and rows from response
    result = response['resultSets'][0]
    headers = result['headers']
    rows = result['rowSet']

    # Convert response to data frame
    result_df = pd.DataFrame(rows)
    result_df.columns = headers

    return result_df