import csv
import json
import time
from pathlib import Path

from src.api import DAILY_VARS, fetch_weather_data
from src.cities import CITIES

RAW_DIR = Path("data/raw")
CSV_PATH = Path("data/processed/weather_2025.csv")
COLUMNS = ["city", "state", "region", "latitude", "longitude", "date", *DAILY_VARS]

RAW_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

write_header = not CSV_PATH.exists()

with CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)
    if write_header:
        writer.writeheader()
        write_header = False

    for city_key, info in CITIES.items():
        city = info.get("city", city_key)
        state = info["state"]
        region = info["region"]
        lat = info["latitude"]
        lon = info["longitude"]
        start = info.get("start_date", "2025-01-01")
        end = info.get("end_date", "2025-12-31")

        json_file = RAW_DIR / f"{city.lower().replace(' ', '_')}.json"

        if json_file.exists():
            data = json.loads(json_file.read_text(encoding="utf-8"))
        else:
            data = fetch_weather_data(lat, lon, start, end)
            json_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            time.sleep(2)

        daily = data["daily"]
        for i, date in enumerate(daily["time"]):
            row = {
                "city": city,
                "state": state,
                "region": region,
                "latitude": lat,
                "longitude": lon,
                "date": date,
            }
            for var in DAILY_VARS:
                row[var] = daily[var][i]
            writer.writerow(row)

        print("Saved:", city)