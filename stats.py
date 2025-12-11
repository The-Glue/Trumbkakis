import pandas as pd

# Load your cleaned CSV
data = pd.read_csv("cleaned_orioles_b7_events.csv")

# Define event keywords
EVENT_KEYWORDS = {
    "out": ["strikeout", "groundout", "popfly", "flyball", "lineout"],
    "single": ["single"],
    "double": ["double"],
    "triple": ["triple"],
    "home_run": ["home run", "homered"],
    "walk": ["walk"],
    "hbp": ["hit by pitch"],
}

# Initialize the player stats DataFrame
player_stats = pd.DataFrame(columns=[
    "PA", "AB", "H", "BB", "HBP", "1B", "2B", "3B", "HR", "RBI",
    "AVG", "OBP", "SLG", "OPS", "BB%", "K%", "ISO"
])
player_stats.index.name = "Player"

# Function to calculate derived stats
def calculate_derived_stats(stats):
    stats["AVG"] = round(stats["H"] / stats["AB"], 3) if stats["AB"] > 0 else 0
    stats["OBP"] = round((stats["H"] + stats["BB"] + stats["HBP"]) / stats["PA"], 3) if stats["PA"] > 0 else 0
    stats["SLG"] = round((stats["1B"] + 2 * stats["2B"] + 3 * stats["3B"] + 4 * stats["HR"]) / stats["AB"], 3) if stats["AB"] > 0 else 0
    stats["OPS"] = round(stats["OBP"] + stats["SLG"], 3)
    stats["BB%"] = round(stats["BB"] / stats["PA"], 3) if stats["PA"] > 0 else 0
    stats["K%"] = round((stats["AB"] - stats["H"]) / stats["PA"], 3) if stats["PA"] > 0 else 0
    stats["ISO"] = round(stats["SLG"] - stats["AVG"], 3) if stats["AB"] > 0 else 0
    return stats

# Iterate through the data
for _, row in data.iterrows():
    batter = row["Batter"]
    event = str(row["Event"]).lower()  # Ensure case-insensitivity

    # Skip rows without a batter
    if pd.isna(batter) or batter.strip() == "":
        continue

    # Add batter to stats DataFrame if not already present
    if batter not in player_stats.index:
        player_stats.loc[batter] = {
            "PA": 0, "AB": 0, "H": 0, "BB": 0, "HBP": 0,
            "1B": 0, "2B": 0, "3B": 0, "HR": 0, "RBI": 0,
            "AVG": 0, "OBP": 0, "SLG": 0, "OPS": 0, "BB%": 0, "K%": 0, "ISO": 0
        }

    # Increment plate appearances
    player_stats.loc[batter, "PA"] += 1

    # Parse the event to update stats
    if any(keyword in event for keyword in EVENT_KEYWORDS["out"]):  # Out
        player_stats.loc[batter, "AB"] += 1

    elif any(keyword in event for keyword in EVENT_KEYWORDS["single"]):  # Single
        player_stats.loc[batter, "AB"] += 1
        player_stats.loc[batter, "H"] += 1
        player_stats.loc[batter, "1B"] += 1

    elif any(keyword in event for keyword in EVENT_KEYWORDS["double"]):  # Double
        player_stats.loc[batter, "AB"] += 1
        player_stats.loc[batter, "H"] += 1
        player_stats.loc[batter, "2B"] += 1

    elif any(keyword in event for keyword in EVENT_KEYWORDS["triple"]):  # Triple
        player_stats.loc[batter, "AB"] += 1
        player_stats.loc[batter, "H"] += 1
        player_stats.loc[batter, "3B"] += 1

    elif any(keyword in event for keyword in EVENT_KEYWORDS["home_run"]):  # Home Run
        player_stats.loc[batter, "AB"] += 1
        player_stats.loc[batter, "H"] += 1
        player_stats.loc[batter, "HR"] += 1
        player_stats.loc[batter, "RBI"] += 1  # Increment RBI directly

    elif any(keyword in event for keyword in EVENT_KEYWORDS["walk"]):  # Walk
        player_stats.loc[batter, "BB"] += 1

    elif any(keyword in event for keyword in EVENT_KEYWORDS["hbp"]):  # Hit By Pitch
        player_stats.loc[batter, "HBP"] += 1

# Calculate derived stats for all players
player_stats = player_stats.apply(calculate_derived_stats, axis=1)

# Convert all integer columns to integers
integer_columns = ["PA", "AB", "H", "BB", "HBP", "1B", "2B", "3B", "HR", "RBI"]
player_stats[integer_columns] = player_stats[integer_columns].astype(int)

# Save to a new CSV
player_stats.to_csv("orioles_b7_leaderboard.csv")

print("Player leaderboard generated and saved to 'player_leaderboard.csv'.")
