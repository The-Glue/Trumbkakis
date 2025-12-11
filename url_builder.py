import requests
from bs4 import BeautifulSoup
import csv

# Dictionary for month-to-number conversion (using first three letters)
months = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

# File to save the aggregated data
output_file = "orioles_home_games_1992_2024.csv"

# Initialize the total game counter
total_games = 0

# Open the CSV file to write results
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Year", "Date", "Boxscore_URL"])  # Header row

    # Loop through years
    for year in range(1992, 2025):
        print(f"Processing year: {year}")
        
        # Construct the URL for the team's schedule
        url = f"https://www.baseball-reference.com/teams/BAL/{year}-schedule-scores.shtml#all_team_schedule"
        
        # Fetch the schedule page
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {year}. Skipping...")
            continue
        
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", id="team_schedule")
        if not table:
            print(f"No schedule table found for {year}. Skipping...")
            continue
        
        # Extract the table rows
        rows = table.find_all("tr")
        
        # Process each row
        for row in rows[1:]:  # Skip the header row
            columns = row.find_all("td")
            if len(columns) > 1:  # Ensure it's a valid row
                date_text = columns[0].text.strip()
                home_away = columns[3].text.strip()
                
                # Process only home games (no '@' in "Home/Away" column)
                if home_away != '@':
                    # Debugging: Show the raw date text
                    print(f"Raw date ({year}): {date_text}")

                    # Remove doubleheader markers (e.g., "(1)", "(2)")
                    clean_date = date_text.replace("(1)", "").replace("(2)", "").strip()
                    parts = clean_date.split()  # Split by spaces

                    if len(parts) >= 2:
                        day = parts[-1]  # Extract the day
                        month = parts[-2][:3]  # First three letters of the month
                        month_num = months.get(month, "00")  # Convert to number

                        # Handle doubleheaders
                        suffix = "0"  # Default suffix
                        if "(1)" in date_text:
                            suffix = "1"
                        elif "(2)" in date_text:
                            suffix = "2"

                        formatted_date = f"{year}{month_num}{day.zfill(2)}"  # Construct YYYYMMDD

                        # Debugging: Show the formatted date
                        print(f"Formatted date ({year}): {formatted_date}")

                        # Construct the boxscore URL
                        boxscore_url = f"https://www.baseball-reference.com/boxes/BAL/BAL{formatted_date}{suffix}.shtml"
                        
                        # Debugging: Show the constructed URL
                        print(f"Constructed URL ({year}): {boxscore_url}")

                        # Write to CSV
                        writer.writerow([year, date_text, boxscore_url])
                        total_games += 1  # Increment the game count

# Debugging: Print the total number of games processed
print(f"Total number of home games processed from 1992 to 2024: {total_games}")
