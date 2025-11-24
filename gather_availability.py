
from pathlib import Path
import requests
import os
from datetime import datetime, timedelta


def request_availability_image(hall_id, date):
    url = "https://asp5.lvp.nl/amisweb/utrecht/amis1/amis.php?action=objschema"
    params = {
        "obj_id": hall_id,
        "date": date,
        "period": 0
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.content  # Return the image content
    except Exception as e:
        print(f"Error fetching availability image: {e}")
        return None



def fetch_hall_images(hall_id, days, start_date, end_date):
    # for each day in the range, fetch and save the image
    dn = Path(f"img/{hall_id}")
    if dn.exists():
        for fn in dn.iterdir():
            fn.unlink()
    dn.mkdir(parents=True, exist_ok=True)
    start_dt = datetime(*start_date)
    end_dt = datetime(*end_date)
    current_dt = start_dt

    while current_dt <= end_dt:
        day_name = current_dt.strftime("%a").lower()[:3]
        if day_name in days:
            date_str = current_dt.strftime("%Y%m%d")
            image_data = request_availability_image(hall_id, int(date_str))
            if image_data:
                filename = f"img/{hall_id}/availability_{date_str}_{day_name}.png"
                with open(filename, "wb") as img_file:
                    img_file.write(image_data)
                print(f"Availability image saved as {filename}")
            else:
                print(f"Failed to retrieve availability image for {date_str} ({day_name})")
        current_dt += timedelta(days=1)

def fetch_data(config):
    def parse_date_tuple(date_str: str) -> tuple[int, int, int]:
        return tuple(map(int, date_str.split("-")))
    
    halls = config.get("hall_ids", [])
    days = config.get("days_of_week", [])
    start_date = parse_date_tuple(config.get("start_date", "1999-01-01"))
    end_date = parse_date_tuple(config.get("end_date", "2000-31-12"))
    for hall_id in halls:
        fetch_hall_images(hall_id, days, start_date, end_date)

if __name__ == "__main__":
    halls = [1000003152, 1000001386, 1000000589, 1000000581]
    days = ["thu"]
    start_date = (2025, 12, 1)
    end_date = (2026, 3, 31)
    for hall_id in halls:
        fetch_hall_images(hall_id, days, start_date, end_date)