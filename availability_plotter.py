from pathlib import Path
import re
from PIL import Image
import io
from datetime import datetime
import time
import calendar
from bs4 import BeautifulSoup

# availability_plotter.py
import matplotlib.pyplot as plt
import requests



def parse_file_name(name: str):
    """return (day, date) from file name"""
    parts = re.split(r'[_\.]', name.lower())
    day = parts[2]
    date = parts[1]
    return (day, date)

def request_and_save_headers(img_dir: Path):
    url = "https://asp5.lvp.nl/amisweb/utrecht/amis1/amis.php"
    params = {
        "action":"objschema",
        "date":"",
        "period":0
    }
    for position in ['header', 'footer']:
        params['obj_id'] = position
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            img_data = response.content
            header_dir = img_dir / 'headers'
            header_dir.mkdir(exist_ok=True)
            with open(header_dir / f"{position}.png", "wb") as f:
                f.write(img_data)
            print(f"Saved {position} header image.")
        except Exception as e:
            print(f"Error fetching {position} header image: {e}")

def load_images_by_day(hall_img_dir: Path):
    hall_img_dir = Path(hall_img_dir)
    if not hall_img_dir.exists():
        raise FileNotFoundError(f"{hall_img_dir} not found")

    day_imgs = {day:[] for day in calendar.day_name}
    for p in hall_img_dir.iterdir():
        if not p.is_file() or p.suffix.lower() != '.png':
            continue
        name = p.stem.lower()
        day, date = parse_file_name(p.name)
        day = [d for d in calendar.day_name if d.lower()[:3] == day][0]
        day_imgs[day].append({"date": date, "path": p})

    day_imgs = {day: sorted(entries, key=lambda e: e["date"]) for day, entries in day_imgs.items()}
    # look for header images (top then bottom) in a "header" subfolder
    header_dir = hall_img_dir.parent /'headers'
    top_header = bottom_header = None
    if not (header_dir.exists() and header_dir.is_dir() and len([d for d in header_dir.iterdir()]) == 2):
        request_and_save_headers(hall_img_dir.parent)
    top_header = header_dir / 'header.png'
    bottom_header = header_dir / 'footer.png'

    def _stack_images_vert(paths, top=None, bottom=None):
        imgs = []
        if top:
            imgs.append(Image.open(top).convert('RGBA'))
        for p in paths:
            imgs.append(Image.open(p).convert('RGBA'))
        if bottom:
            imgs.append(Image.open(bottom).convert('RGBA'))
        if not imgs:
            return None
        max_w = max(im.width for im in imgs)
        total_h = sum(im.height for im in imgs)
        canvas = Image.new('RGBA', (max_w, total_h), (255, 255, 255, 0))
        y = 0
        for im in imgs:
            x = (max_w - im.width) // 2
            canvas.paste(im, (x, y), im)
            y += im.height
        bio = io.BytesIO()
        canvas.save(bio, format='PNG')
        bio.seek(0)
        return bio

    # create single stacked image per day (so all saturday images appear in one plot)
    res = {day: {"dates": [e["date"] for e in entries], "img": _stack_images_vert([e["path"] for e in entries] , top=top_header, bottom=bottom_header)} for day, entries in day_imgs.items() if entries}
    
    return res

def retrieve_hall_name(hall_id: int) -> str:
    import requests
    url = "https://asp5.lvp.nl/amisweb/utrecht/amis1/amis.php?action=objinfo"
    params = {
        "obj_id": hall_id
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        # parse the html page and look for the <address> tag and extract the text contents
        soup = BeautifulSoup(response.text, 'html.parser')
        address_tag = soup.find('address').find('strong')
        return address_tag.get_text(strip=True) if address_tag else f"Hall_{hall_id}"
    except Exception as e:
        return f"Hall_{hall_id}"

def plot_week_overview(img_dir: Path, hall_name: str):
    dates_and_images_by_day = load_images_by_day(img_dir)
    l = len(dates_and_images_by_day)
    nd = len(list(dates_and_images_by_day.values())[0]["dates"])
    n_rows = (l + 1) // 2
    fig, axes = plt.subplots(n_rows, (2 if l >= 2 else 1), figsize=(15 if l >=2 else 8, 1 + (nd+2)*.3 * n_rows))
    # normalize axes shape (handles rows == 1)
    if ( l >2 and (l %2) ==1):
        axes[-1,-1].remove()
    # column titles
    for i,day in enumerate(dates_and_images_by_day.keys()):

        record = dates_and_images_by_day[day]
        ax: plt.Axes
        if l == 1:
            ax = axes
        elif l == 2:
            ax = axes[i]
        else:
            ax = axes[i // 2, i % 2]

        ax.set_title(day)
        # plot image
        img = Image.open(record["img"]).convert('RGBA')
        formatted_dates = [datetime.strptime(d, "%Y%m%d").strftime("%d %b") for d in record["dates"]]

        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks(list(range(10,img.height, img.height//(len(record["dates"])+2))), labels=["",*formatted_dates,""])
        ax.set_xlabel('Time')



    fig.subplots_adjust(top=0.9)
    fig.suptitle(f'Availability overview {hall_name}', fontsize=16, y=0.95)
    # plt.tight_layout()
    return fig

def plot_all_halls(img_folder: Path):
     for hall_dir in (hall_dir for hall_dir in img_folder.iterdir() if hall_dir.is_dir() and hall_dir.name.isdigit()):
        hall_id = int(hall_dir.name)
        hall_name = retrieve_hall_name(hall_id)
        fig = plot_week_overview(hall_dir, hall_name)
        fn = f'img/availability_overview_{hall_id}_{hall_name}.png'
        Path(fn).unlink(missing_ok=True)
        fig.savefig(fn)

if __name__ == '__main__':
    img_folder = Path('img')
    plot_all_halls(img_folder)