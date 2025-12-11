import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the player stats DataFrame
player_stats = pd.read_csv("orioles_b7_leaderboard.csv", index_col="Player")

# --- DATA PREPARATION (Ensure all extreme points are included) ---
# Group by PA and find the min/max OPS in each group
idx_max = player_stats.groupby(['PA'])['OPS'].idxmax()
idx_min = player_stats.groupby(['PA'])['OPS'].idxmin()

# Also include the absolute overall min/max OPS players
idx_absolute_max = player_stats['OPS'].idxmax()
idx_absolute_min = player_stats['OPS'].idxmin()

# Combine all indices
players_to_label_indices = pd.Index(
    idx_max.tolist() + 
    idx_min.tolist() + 
    [idx_absolute_max, idx_absolute_min]
).unique()

players_to_label_df = player_stats.loc[players_to_label_indices].copy()
players_to_label_df = players_to_label_df.sort_values(by="OPS", ascending=False)
# --- DATA PREPARATION END ---


# --- PLOT SETUP ---
plt.figure(figsize=(12, 7))
plt.scatter(player_stats["PA"], player_stats["OPS"], alpha=0.7, color="blue", edgecolors="black")
plt.xlabel("Plate Appearances (PA)", fontsize=12)
plt.ylabel("On-base Plus Slugging (OPS)", fontsize=12)
plt.title("PA Leading off Bottom of 7th inning at Camden Yards vs. OPS, 1992-2025", fontsize=14)


# --- ANNOTATION WITH SCALED PROXIMITY FILTER ---
labeled_coords = []
# Factor to scale the PA distance by. Adjust if your plot is too crowded or too sparse.
PA_SCALE_FACTOR = 10 

# Adjusted threshold for the scaled coordinates
MIN_DISTANCE_THRESHOLD = 0.5 


for player, row in players_to_label_df.iterrows():
    # Scale x for distance calculation only
    x_raw, y = row["PA"], row["OPS"]
    x_scaled = x_raw / PA_SCALE_FACTOR
    
    should_label = True
    
    # Check the distance to every previously labeled point
    for lx_scaled, ly in labeled_coords:
        # Calculate the Euclidean distance using the SCALED X-coordinate
        distance = np.sqrt((x_scaled - lx_scaled)**2 + (y - ly)**2)
        
        if distance < MIN_DISTANCE_THRESHOLD:
            should_label = False
            break
            
    if should_label:
        # 1. Label the point using the RAW coordinates
        plt.annotate(
            player, 
            (x_raw, y), 
            fontsize=9, 
            alpha=0.9,
            textcoords="offset points", 
            xytext=(5, 5)
        )
        # 2. Add the labeled point's SCALED coordinates to our list
        labeled_coords.append((x_scaled, y))

# Show grid
plt.grid(alpha=0.3)
plt.tight_layout()

# --- NEW LINE TO SAVE AND SHOW THE IMAGE ---
# Use savefig() to save the file, and plt.show() to display it. dpi=300 ensures high resolution.
plt.savefig("orioles_b7_graph.png", dpi=300) 
print("\nGraph saved successfully to 'orioles_b7_graph.png'")
# Now, display the plot on the screen.
plt.show()
