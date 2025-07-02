from dataclasses import dataclass, asdict, is_dataclass, field
from datetime import datetime
import hashlib
import json
import os
import re
import urllib.request

from Crypto.Cipher import AES


@dataclass
class Game:
    encrypted_game_id: str
    description: str
    title_id: str = None
    type: str = None
    min_os: str = None
    regions: list[str] = field(default_factory=list)
    distribution: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    catridge_description: str = None


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


# URL to get the list of games from
switchbrew_url = "https://switchbrew.org/w/index.php?title=Title_list/Games"
manual_games_url = "https://raw.githubusercontent.com/RenanGreca/Switch-Screenshots/master/game_ids.json"

# md5 checksum of the keys.prod file
keys_prod_md5sum = "f97a6841063b72f6a5d7f7e0df5bb886"


def get_key():
    assert (
        "KEYS_PROD" in os.environ
    ), "KEYS_PROD environment variable needs to be defined"
    key = os.environ["KEYS_PROD"]
    checksum = hashlib.md5(key.encode("utf-8")).hexdigest()
    assert checksum == keys_prod_md5sum, "KEYS_PROD value checksum didn't match"
    return bytes.fromhex(key)


def download_url(url):
    with urllib.request.urlopen(url) as f:
        result = f.read().decode("utf-8")
    return result


def clear_html_tags(html):
    clean_regex = re.compile("<.*?>")
    return re.sub(clean_regex, "", html)


def encrypt_title_id(title_id):
    title_id = bytes.fromhex(title_id)[7::-1]  # Reversed bytes
    title_id = title_id.hex().ljust(32, "0")  # Pad with zeroes in hexadecimal
    title_id = bytes.fromhex(title_id)  # Convert to bytes
    encrypted = cipher.encrypt(title_id)  # Encrypt using prod.keys
    return encrypted.hex().upper()


def get_games_switchbrew():
    return []
    html = download_url(switchbrew_url)
    tr_regex = re.compile(
        r"<tr>(\n<td>.*</td>\n<td>.*</td>\n<td>.*</td>\n<td>.*</td>\n<td>.*</td>\n<td>.*</td>\n<td>.*</td>\n<td>.*\n</td>)",
        re.MULTILINE,
    )
    td_regex = re.compile(r"<td>.*\n?</td>")
    for match in tr_regex.findall(html):
        yield [clear_html_tags(cell).strip() for cell in td_regex.findall(match)]


def get_games_manual():
    contents = download_url(manual_games_url)
    return json.loads(contents)


def find_game_by_id(games, id) -> int:
    i = 0
    for game in games:
        if game.title_id == id:
            return i
        i += 1


if __name__ == "__main__":
    cipher = AES.new(get_key(), AES.MODE_ECB)
    games = []
    for game in get_games_switchbrew():
        games.append(
            Game(
                title_id=game[0],
                description=game[1],
                regions=game[2].split(" "),
                min_os=game[3],
                distribution=[d.strip() for d in game[4].split("/")],
                versions=game[5].split(" "),
                cartridge_description=game[6],
                type=game[7],
                encrypted_game_id=encrypt_title_id(game[0]),
            )
        )

    for encrypted_game_id, name in get_games_manual().items():
        game_index = find_game_by_id(games, encrypted_game_id)
        game = Game(encrypted_game_id=encrypted_game_id, description=name)
        if game_index:
            games[game_index] = game
        else:
            games.append(game)

    with open("public/switch_games.json", "w") as handler:
        json.dump(games, handler, cls=DataclassJSONEncoder)

    with open("public/switch_id_names.json", "w") as handler:
        games_id_and_names = [
            {
                "encrypted_game_id": game.encrypted_game_id,
                "title_normalized": game.description,
            }
            for game in games
        ]
        json.dump(games_id_and_names, handler)

    with open("index.html.tmpl", "rb") as handler:
        index_html = handler.read()

        with open("public/index.html", "w") as handler_writter:
            handler_writter.write(
                index_html.decode("utf-8").format(last_update=datetime.utcnow())
            )
