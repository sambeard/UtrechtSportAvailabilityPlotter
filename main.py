from gather_availability import fetch_data
from availability_plotter import plot_all_halls
import json
import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch availability data for sport halls based on configuration file.")
    parser.add_argument("config", type=str, help="Path to the configuration JSON file.", default="configs/template.json", nargs="?")
    parser.add_argument("--no-fetch", action="store_true", help="Should not fetch availability data before plotting?")
    args = parser.parse_args()
    config_path = args.config
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        if(not args.no_fetch):
            fetch_data(config)
        # After fetching data, generate plots for each hall
        img_folder = Path('img')
        plot_all_halls(img_folder)
