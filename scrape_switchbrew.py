from dataclasses import dataclass, asdict, is_dataclass, field
from datetime import datetime, timezone
import json
import re
import urllib.request
from typing import Optional


@dataclass
class Game:
    program_id: str  # This is the title_id/ProgramId from the table
    description: str
    title_normalized: Optional[str] = None
    type: Optional[str] = None
    min_os: Optional[str] = None
    regions: list[str] = field(default_factory=list)
    distribution: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    cartridge_description: Optional[str] = None


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        return super().default(o)


# URL to get the list of games from
switchbrew_url = "https://switchbrew.org/w/index.php?title=Title_list/Games"


def download_url(url):
    with urllib.request.urlopen(url) as f:
        result = f.read().decode("utf-8")
    return result


def clear_html_tags(html):
    clean_regex = re.compile("<.*?>")
    return re.sub(clean_regex, "", html)


def normalize_title(title):
    """
    Normalize game titles by:
    - Removing trademark symbols (™, ®)
    - Removing region indicators in parentheses
    - Cleaning up extra spaces
    - Removing special characters that might cause issues
    """
    # Remove trademark and registered symbols
    normalized = title.replace('™', '').replace('®', '')
    
    # Remove content in parentheses (often region/language indicators)
    normalized = re.sub(r'\s*\([^)]*\)', '', normalized)
    
    # Remove content in square brackets
    normalized = re.sub(r'\s*\[[^\]]*\]', '', normalized)
    
    # Clean up multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def get_games_switchbrew():
    html = download_url(switchbrew_url)
    # Updated regex to match the actual table structure
    tr_regex = re.compile(
        r"<tr>(\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?</td>\n<td>.*?\n?</td>)",
        re.MULTILINE | re.DOTALL,
    )
    td_regex = re.compile(r"<td>.*?\n?</td>", re.DOTALL)
    
    games = []
    for match in tr_regex.findall(html):
        cells = [clear_html_tags(cell).strip() for cell in td_regex.findall(match)]
        if len(cells) >= 8:  # Ensure we have all required fields
            games.append(cells)
    
    return games


if __name__ == "__main__":
    print("Scraping SwitchBrew for Nintendo Switch game data...")
    
    games = []
    for game_data in get_games_switchbrew():
        # Skip header rows or invalid data
        if game_data[0].lower() == "programid" or not game_data[0]:
            continue
            
        game = Game(
            program_id=game_data[0],  # ProgramId (title_id)
            description=game_data[1],  # Description
            title_normalized=normalize_title(game_data[1]),  # Normalized title
            regions=game_data[2].split(" ") if game_data[2] else [],  # Region
            min_os=game_data[3] if game_data[3] else None,  # Minimum Required OS
            distribution=[d.strip() for d in game_data[4].split("/")] if game_data[4] else [],  # Distribution Method
            versions=game_data[5].split(" ") if game_data[5] else [],  # Versions
            cartridge_description=game_data[6] if game_data[6] else None,  # Cartridge Description
            type=game_data[7] if len(game_data) > 7 and game_data[7] else None,  # Type
        )
        games.append(game)
    
    print(f"Found {len(games)} games")
    
    # Create public directory if it doesn't exist
    import os
    os.makedirs("public", exist_ok=True)
    
    # Save to JSON file
    with open("public/switchbrew_games.json", "w") as handler:
        json.dump(games, handler, cls=DataclassJSONEncoder, indent=2)
    
    # Also save a simple mapping of program_id to game name
    with open("public/switchbrew_id_names.json", "w") as handler:
        games_id_and_names = [
            {
                "program_id": game.program_id,
                "name": game.description,
                "title_normalized": game.title_normalized,
            }
            for game in games
        ]
        json.dump(games_id_and_names, handler, indent=2)
    
    # Generate index.html if template exists
    try:
        with open("index.html", "rb") as handler:
            index_html = handler.read()
            with open("public/index.html", "w") as handler_writer:
                handler_writer.write(
                    index_html.decode("utf-8").format(last_update=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
                )
        print("Generated public/index.html")
    except FileNotFoundError:
        print("index.html not found, skipping index.html generation")
    
    print("Data saved to public/switchbrew_games.json and public/switchbrew_id_names.json")