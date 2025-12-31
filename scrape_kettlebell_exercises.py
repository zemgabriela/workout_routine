import requests
from bs4 import BeautifulSoup
import os
import re

# ---------------- CONFIG ---------------- #
BASE_URL = "https://liftmanual.com/strength/#K-letter"
OUTPUT_DIR = "kettlebell_exercises"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- FETCH MAIN PAGE ---------------- #
response = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, 'html.parser')

# Find K-letter section
k_header = soup.find('h2', id='K-letter')
if not k_header:
    print("K-letter header not found.")
    exit(1)

ul = k_header.find_next('ul')
if not ul:
    print("K-letter exercise list not found.")
    exit(1)

exercise_links = ul.find_all('a')
print(f"Found {len(exercise_links)} kettlebell exercise links.")

# ---------------- LOOP EXERCISES ---------------- #
for link in exercise_links:
    ex_url = link['href']
    ex_name = link.get_text(strip=True)
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', ex_name)

    print(f"Processing: {ex_name}")

    ex_resp = requests.get(ex_url, headers=HEADERS)
    ex_soup = BeautifulSoup(ex_resp.text, 'html.parser')

    desc = ""
    muscle = ""

    p_tags = ex_soup.find_all('p')

    # ---- Description ----
    for idx, p in enumerate(p_tags):
        strong = p.find('strong')
        if strong and 'description' in strong.get_text(strip=True).lower():
            next_p = p.find_next_sibling('p')
            if next_p and not next_p.find('strong'):
                desc = next_p.get_text(strip=True)
            else:
                for j in range(idx + 1, min(idx + 4, len(p_tags))):
                    if not p_tags[j].find('strong'):
                        desc = p_tags[j].get_text(strip=True)
                        break
            break

    if not desc:
        for p in p_tags:
            text = p.get_text(strip=True)
            if text and "description" not in text.lower():
                desc = text
                break

    # ---- Muscle Group ----
    for idx, p in enumerate(p_tags):
        strong = p.find('strong')
        if strong and 'muscle' in strong.get_text(strip=True).lower():
            next_p = p.find_next_sibling('p')
            if next_p and not next_p.find('strong'):
                muscle = next_p.get_text(strip=True)
            else:
                for j in range(idx + 1, min(idx + 4, len(p_tags))):
                    if not p_tags[j].find('strong'):
                        muscle = p_tags[j].get_text(strip=True)
                        break
            break

    # ---------------- IMAGE EXTRACTION ---------------- #
    img_url = ""
    img_path = ""

    header_container = ex_soup.find('div', class_='workoutheader')
    if header_container:
        img_tag = header_container.find('img')
        if img_tag:
            img_url = (
                img_tag.get("src")
                or img_tag.get("data-src")
                or img_tag.get("data-lazy-src")
            )

            if img_url and "data:image" in img_url:
                img_url = img_tag.get("data-src") or img_tag.get("data-lazy-src")

            if img_url and not img_url.startswith("http"):
                img_url = "https://liftmanual.com" + img_url

    # ---------------- DOWNLOAD IMAGE ---------------- #
    if img_url:
        try:
            img_resp = requests.get(img_url, headers=HEADERS)
            if img_resp.status_code == 200:
                img_path = os.path.join(OUTPUT_DIR, f"{safe_name}.jpg")
                with open(img_path, "wb") as f:
                    f.write(img_resp.content)
            else:
                print(f"Image not found ({img_resp.status_code}) for {ex_name}")
        except Exception as e:
            print(f"Failed to download image for {ex_name}: {e}")
    else:
        print(f"No image found for {ex_name}")

    # ---------------- SAVE TEXT FILE ---------------- #
    with open(os.path.join(OUTPUT_DIR, f"{safe_name}.txt"), "w", encoding="utf-8") as f:
        f.write(f"Name: {ex_name}\n")
        f.write(f"Description: {desc}\n")
        f.write(f"Muscle Group: {muscle}\n")
        f.write(f"Image: {img_path}\n")

print(f"\n✅ Scraped {len(exercise_links)} kettlebell exercises.")