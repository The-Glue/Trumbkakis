import requests
from bs4 import BeautifulSoup, Comment
import csv
import time

def fetch_b7_event_bref(game_url):
    print(f"Requesting URL: {game_url}")
    
    try:
        response = requests.get(game_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from {game_url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the Play-by-Play section
    play_by_play_section = soup.find("div", {"id": "all_play_by_play"})
    if not play_by_play_section:
        print(f"No Play-by-Play section found for {game_url}")
        return None

    # Locate the table in the comments
    comments = play_by_play_section.find_all(string=lambda text: isinstance(text, Comment))
    play_by_play_html = None

    for comment in comments:
        if "table" in comment:  # Look for the table in comments
            play_by_play_html = BeautifulSoup(comment, 'html.parser')
            break

    if not play_by_play_html:
        print(f"No Play-by-Play table found in comments for {game_url}")
        return None

    # Extract the table
    pbp_table = play_by_play_html.find("table")
    if not pbp_table:
        print(f"No Play-by-Play table found for {game_url}")
        return None

    # Find "Bottom of the 7th" header
    rows = pbp_table.find_all("tr")
    bottom_7th_found = False
    for row in rows:
        header = row.find("th", {"scope": "row"})
        if header:
            header_text = header.get_text(strip=True)
            if "Bottom of the 7th" in header_text:
                bottom_7th_found = True
                continue

        # If "Bottom of the 7th" header is found, process subsequent rows
        if bottom_7th_found:
            cells = row.find_all("td")
            if cells:  # Only process rows with data
                event_data = [cell.get_text(strip=True) for cell in cells]
                
                # Skip rows that are just empty placeholders or summaries
                if len(event_data) > 10 and event_data[10]:  # Assuming the event description is in the 11th column (index 10)
                    return event_data

    return None


def process_games_from_csv(input_file, output_file):
    # Initialize new data list with headers
    data = [["Date", "Boxscore_URL", "Inning", "Outs", "Base State", "Pitches", "Event Type", "Team", "Batter", "Pitcher", "Win Expectancy", "Leverage Index", "Event"]]

    # Read game URLs from input CSV
    with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        games = list(reader)

    for index, game in enumerate(games):
        game_url = game["Boxscore_URL"]
        date = game["Date"]

        # Fetch the b7 event
        print(f"Processing game on {date}...")
        b7_event = fetch_b7_event_bref(game_url)
        if b7_event:
            # Align columns properly
            row_data = [date, game_url] + b7_event
            data.append(row_data)
        
        # Save progress every 10 games
        if index % 10 == 0:
            print(f"Saving progress after processing {index} games...")
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(data)
            print(f"Progress saved after {index} games.")

        # Delay to avoid rate-limiting
        print("Waiting 5 seconds before the next request...")
        time.sleep(5)

    # Final save
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print(f"Finished processing games. Data saved to '{output_file}'.")


# Input and output file paths
input_file = "orioles_home_games_1992_2024.csv"
output_file = "orioles_b7_events.csv"

# Process the games
process_games_from_csv(input_file, output_file)
