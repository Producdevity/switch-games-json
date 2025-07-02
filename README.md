# Switch Games JSON

**This is a fork of [fmartingr/switch-games-json](https://github.com/fmartingr/switch-games-json)**

:warning: **NOTICE:** The original repository was archived and read-only because Nintendo now provides a better method to get Switch game screenshots with folder names. [Please refer to the Nintendo documentation](https://en-americas-support.nintendo.com/app/answers/detail/a_id/53664/~/how-to-transfer-screenshots-and-video-captures-to-a-computer-via-a-usb-cable) to learn more.

## Why This Fork Exists

While the original purpose of mapping screenshot folders is now solved by Nintendo, this database remains valuable for the emulation community. This fork was created to support [EmuReady](https://emuready.com) ([GitHub](https://github.com/Producdevity/EmuReady)), a community-driven platform for tracking emulation compatibility across different devices and emulators.

The unencrypted program IDs in this database enable EmuReady to:

- Launch games directly in Switch emulators like [Eden](https://eden-emu.dev/)
- Track game compatibility across different emulators
- Provide accurate game information for the community

This clean, accessible data helps make emulation more user-friendly and supports the preservation of gaming history.

---

## Switch Games JSON

This repository contains the code to parse and build a Nintendo Switch game list in JSON using the [Game List from SwitchBrew](https://switchbrew.org/w/index.php?title=Title_list/Games).

There are two resulting JSON files:

- `switchbrew_games.json`: Contains all game information from SwitchBrew including program IDs, descriptions, regions, versions, etc.
- `switchbrew_id_names.json`: Simple mapping of `program_id`, `name`, and `title_normalized`.

## Where to obtain the list?

List is published in the GitHub Pages for this repository and can be downloaded at [https://producdevity.github.io/switch-games-json/](https://producdevity.github.io/switch-games-json/), just point to the file that best suits your use case.

List is updated weekly via GitHub Actions.

## Schema

```json
# switchbrew_games.json
{
    "program_id": "0100000000010000",
    "description": "Super Mario Odyssey™",
    "title_normalized": "Super Mario Odyssey",
    "type": "Application / Game",
    "min_os": "3.0.1",
    "regions": [
        "CHN",
        "EUR",
        "JPN",
        "KOR",
        "USA"
    ],
    "distribution": [
        "Digital",
        "Cartridge"
    ],
    "versions": [
        "0",
        "0x10000",
        "0x20000",
        "0x30000",
        "0x40000"
    ],
    "cartridge_description": null
}
```

```json
# switchbrew_id_names.json
{
    "program_id": "0100000000010000",
    "name": "Super Mario Odyssey™",
    "title_normalized": "Super Mario Odyssey"
}
```

## Running Locally

```bash
# Clone the repository
git clone https://github.com/Producdevity/switch-games-json.git
cd switch-games-json

# Run the scraper (no dependencies required)
python scrape_switchbrew.py

# Files will be generated in the public/ directory
# - public/switchbrew_games.json
# - public/switchbrew_id_names.json
# - public/index.html

# Test locally
cd public
python -m http.server 8000
# Visit http://localhost:8000
```

## Acknowledgements

- [fmartingr](https://github.com/fmartingr/switch-games-json): Original repository and concept
- [SwitchBrew](https://switchbrew.org/): Source of Nintendo Switch game data
- [s1cp/nxshot](https://github.com/s1cp/nxshot): Original work on calculating the switch encrypted title IDs
- [RenanGreca](https://github.com/RenanGreca/Switch-Screenshots): Community provided game IDs
