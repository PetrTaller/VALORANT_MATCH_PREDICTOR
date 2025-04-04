import requests
from bs4 import BeautifulSoup
import csv
import json
import re

# File paths
TEAMS_FILE = "teams.csv"
LEAGUES_FILE = "leagues.csv"
MAPS_FILE = "maps.csv"

# --- Load teams from CSV ---
def load_teams():
    teams = {}
    last_id = 0
    try:
        with open(TEAMS_FILE, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) == 2:
                    team_name = row[1].strip().lower()  # Normalize team name (lowercase and strip whitespace)
                    teams[team_name] = int(row[0])
                    last_id = max(last_id, int(row[0]))
    except FileNotFoundError:
        pass  # If the file doesn't exist, just return empty dict
    return teams, last_id

# --- Save teams to CSV --- 
def save_teams(teams):
    with open(TEAMS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "team"])  # Header
        for team_name, team_id in teams.items():
            writer.writerow([team_id, team_name])

# Example function to update teams after parsing a match
def update_teams(teams):
    global team_dict, team_counter
    for team_name in teams:
        team_name_lower = team_name.strip().lower()  # Normalize team name (lowercase and strip whitespace)
        if team_name_lower not in team_dict:
            team_counter += 1
            team_dict[team_name_lower] = team_counter  # Assign new ID
    save_teams(team_dict)  # Save teams after the update

# --- Load leagues from CSV ---
def load_leagues():
    leagues = {}
    try:
        with open(LEAGUES_FILE, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) == 2:
                    leagues[row[1].lower()] = int(row[0])
    except FileNotFoundError:
        pass  # If the file doesn't exist, just return empty dict
    return leagues

# --- Load maps from CSV ---
def load_maps():
    maps = {}
    try:
        with open(MAPS_FILE, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) == 2:
                    maps[row[1].upper()] = int(row[0])  # Normalize to uppercase
    except FileNotFoundError:
        pass  # If the file doesn't exist, just return empty dict
    return maps

# Load mapping data
team_dict, team_counter = load_teams()
league_dict = load_leagues()
map_dict = load_maps()

def parse_match(url):
    """
    Fetches the match page at 'url' and extracts key data.
    """
    global team_dict, team_counter
    print(f"Fetching {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} (status code: {response.status_code})")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
   # --- Extract teams ---
    team_elements = soup.find_all('a', class_="match-header-link")
    teams = []
    for a in team_elements:
        name_div = a.find('div', class_=re.compile("wf-title-med"))
        if name_div:
            team_name = name_div.get_text(strip=True)

            # Update the teams list (but use team ID later)
            teams.append(team_name)

    teams = teams[:2] if len(teams) >= 2 else teams  # Ensure only two teams are added

    # --- Extract scores ---
    scores = []
    score_elements = soup.find_all(['span'], class_=re.compile("match-header-vs-score-(winner|loser)"))
    
    if len(score_elements) >= 2:
        try:
            scores = [int(score_elements[0].get_text(strip=True)), int(score_elements[1].get_text(strip=True))]
        except ValueError:
            scores = []
    elif len(score_elements) == 0:
        scores = [1,1]

    # --- Extract date ---
    date_text = ""
    date_container = soup.find('div', class_="match-header-date")
    if date_container:
        date_div = date_container.find('div', attrs={"data-moment-format": "dddd, MMMM Do"})
        if date_div:
            full_date = date_div.get_text(strip=True)
            date_text = full_date.split(",")[1].strip() if "," in full_date else full_date

    # --- extract year and change format of date ---
    date = None
    year = None
    year_pattern = r"-20\d{2}"
    match = re.search(year_pattern, url)
    if match:
        year = match.group(0)[1:]  # Returns the matched year (e.g., '-2025')

    if date_text:
        # Remove the "th", "st", "nd", or "rd" suffix from the day
        day = re.sub(r"(st|nd|rd|th)", "", date_text.split()[1])

        # Convert month name to month number
        month_name = date_text.split()[0]
        month_dict = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08", "September": "09",
            "October": "10", "November": "11", "December": "12"
        }
        month = month_dict.get(month_name, "01")  # Default to "01" if the month name is not found

        # Step 3: Combine into DD-MM-YYYY format
        if year:
            date = f"{day}-{month}-{year}"




    # --- Extract patch version ---
    patch = None
    patch_string = soup.find(string=re.compile(r"Patch\s*[\d\.]+"))
    if patch_string:
        m = re.search(r"Patch\s*([\d\.]+)", patch_string)
        if m:
            try:
                patch = float(m.group(1))
            except ValueError:
                patch = None

        # --- Extract maps ---
    maps = {"map1": None, "map2": None, "map3": None}
    note_div = soup.find('div', class_="match-header-note")
    if note_div:
        note_text = note_div.get_text(";", strip=True)
        picks = re.findall(r"pick\s+([A-Za-z0-9]+)", note_text)

        # Find remaining map
        remaining_match = re.search(r"([A-Za-z0-9]+)\s+remains", note_text)
        remaining_map = remaining_match.group(1).upper() if remaining_match else None

        # Assign map IDs based on CSV mappings
        map_ids = [map_dict.get(m.upper()) for m in picks if m.upper() in map_dict]
        remaining_map_id = map_dict.get(remaining_map)

        if scores in ([0,1], [1,0]):  # BO1 - only 1 map played
            maps["map1"] = remaining_map_id if remaining_map_id else (map_ids[0] if map_ids else None)

        elif scores in ([0,2], [2,0]):  # BO3 but only 2 maps played
            maps["map1"] = map_ids[0] if len(map_ids) >= 1 else None
            maps["map2"] = map_ids[1] if len(map_ids) >= 2 else None
            maps["map3"] = None  

        else:  # Full BO3
            maps["map1"] = map_ids[0] if len(map_ids) >= 1 else None
            maps["map2"] = map_ids[1] if len(map_ids) >= 2 else None
            maps["map3"] = remaining_map_id if remaining_map_id else None

    # --- Find avg kd of teams ----
    kd_acs_spans = soup.find_all("span", class_="side mod-side mod-both")

    # Extract the text content and convert it to floats, checking if conversion is possible
    kd_acs = []
    for span in kd_acs_spans:
        text = span.get_text(strip=True)
        try:
            # Try to convert the text to a float
            kd_acs.append(float(text))
        except ValueError:
            # If it can't be converted to a float, skip the value (no value to extract)
            continue

    if len(kd_acs) >= 60:  # Assuming you expect at least 60 values for KD/ACS
        # Compute the required averages
        avg_kd1 = sum(kd_acs[i] for i in [30, 33, 36, 39, 42]) / 5
        avg_acs1 = sum(kd_acs[i] for i in [31, 34, 37, 40, 43]) / 5
        avg_kd2 = sum(kd_acs[i] for i in [45, 48, 51, 54, 57]) / 5
        avg_acs2 = sum(kd_acs[i] for i in [46, 49, 52, 55, 58]) / 5
    else:
        # Handle the case where there are not enough KD/ACS values
        avg_kd1 = avg_acs1 = avg_kd2 = avg_acs2 = None


    # --- Find the winner ---
    winner = None
    if scores != []:
        if scores[0] > scores[1]:
            winner = 1
        elif scores[0] < scores[1]:
            winner = 0
        elif scores[0] == scores[1]:
            winner = 0.5
    elif scores == []:
        winner = 0.5
    elif scores == None:
        winner = 0.5

    
    # --- Extract league ---
    league = None
    league_pattern = "|".join(re.escape(l) for l in league_dict.keys())
    match = re.search(league_pattern, url, re.IGNORECASE)
    if match:
        league = league_dict.get(match.group(0).lower())
    update_teams(teams)
    # Map teams to numbers using team_dict
    team1_id = team_dict.get(teams[0].strip().lower()) if len(teams) > 0 else None
    team2_id = team_dict.get(teams[1].strip().lower()) if len(teams) > 1 else None

    match_data = {
        "match_url": url,
        "team1": team1_id,
        "team2": team2_id,
        "score1": scores[0] if len(scores) > 0 else None,
        "score2": scores[1] if len(scores) > 1 else None,
        "AVG_KD1": avg_kd1,
        "AVG_KD2": avg_kd2,
        "AVG_ACS1": avg_acs1,
        "AVG_ACS2": avg_acs2,
        "map1": maps.get("map1"),
        "map2": maps.get("map2"),
        "map3": maps.get("map3"),
        "patch": patch,
        "date": date,
        "league" : league,
        "winner": winner
    }
    return match_data


def main():
    matches_data = []
    
    # Read URLs from matches.csv (one URL per line).
    try:
        with open("matches.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    url = row[0].strip()
                    if url:
                        data = parse_match(url)
                        if data:
                            matches_data.append(data)
    except FileNotFoundError:
        print("The file matches.csv was not found.")
        return

    # Write the data to matches.json.
    with open("matches.json", "w", encoding="utf-8") as outfile:
        json.dump(matches_data, outfile, indent=4)
    print("Data extraction complete. Output saved to matches.json")

if __name__ == "__main__":
    main()