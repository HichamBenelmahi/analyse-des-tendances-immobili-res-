from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
import time
import json
import re
import os
from bs4 import BeautifulSoup

# =========================================================
# CONFIG
# =========================================================
URL_BASE = ("https://www.mubawab.ma/fr/cc/immobilier-a-louer-all"
            ":ci:1050,1323,417,824"
            ":sc:apartment-rent,commercial-rent,farm-rent,house-rent,land-rent,office-rent,riad-rent,villa-rent")

MAX_ANNONCES = 5000
MAX_PAGES = 400
BACKUP_EVERY = 50
RESTART_EVERY = 200

OUT_FILE = "annonces_location_all.json"
BACKUP_FILE = "annonces_location_all_backup.json"
PROGRESS_FILE = "progress_location.json"

# =========================================================
# CHROME CONFIG (SPEED + STABILITY)
# =========================================================
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.page_load_strategy = "eager"

prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
    "profile.managed_default_content_settings.fonts": 2,
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())

def start_driver():
    d = webdriver.Chrome(service=service, options=chrome_options)
    d.set_page_load_timeout(30)
    return d

driver = start_driver()

# =========================================================
# LOAD/SAVE (DATA + PROGRESS)
# =========================================================
def load_locations():
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_locations(locations, backup=False):
    path = BACKUP_FILE if backup else OUT_FILE
    with open(path, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=4)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"page": 1, "compteur": 0}

def save_progress(page, compteur):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"page": page, "compteur": compteur}, f, ensure_ascii=False, indent=2)

def infer_compteur_from_data(locations):
    # si on a déjà des annonces, on récupère le max id
    max_id = 0
    for k, v in locations.items():
        try:
            max_id = max(max_id, int(v.get("id", 0)))
        except Exception:
            pass
    return max_id

# =========================================================
# RESTART DRIVER
# =========================================================
def restart_driver():
    global driver
    try:
        driver.quit()
    except Exception:
        pass
    time.sleep(4)
    driver = start_driver()
    print("🔄 Chrome redémarré")

# =========================================================
# SAFE GET (handles dead session)
# =========================================================
def safe_get(url, retries=3, sleep_between=2):
    global driver
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except InvalidSessionIdException:
            print("💥 InvalidSessionId → restart")
            restart_driver()
        except WebDriverException as e:
            msg = str(e).lower()
            if "invalid session id" in msg or "disconnected" in msg or "not connected" in msg:
                print("💥 Chrome disconnected → restart")
                restart_driver()
            else:
                print(f"⚠ WebDriverException ({i+1}/{retries}) → retry...")
                time.sleep(sleep_between)
        except Exception:
            print(f"⚠ Timeout ({i+1}/{retries}) → retry...")
            time.sleep(sleep_between)
    return False

# =========================================================
# HELPERS
# =========================================================
def clean_text(s):
    if not s:
        return None
    return re.sub(r"\s+", " ", s).strip()

def extract_surface(soup):
    try:
        for s in soup.select("div.adDetailFeature span"):
            t = clean_text(s.get_text(" ", strip=True))
            if t and ("m²" in t or "m2" in t):
                return t
    except Exception:
        pass
    return None

def extract_type_bien(soup):
    try:
        for f in soup.select("div.adMainFeature"):
            label = f.select_one("p.adMainFeatureContentLabel")
            value = f.select_one("p.adMainFeatureContentValue")
            if label and value and "Type de bien" in label.get_text():
                return clean_text(value.get_text(" ", strip=True))
    except Exception:
        pass
    return None

def extract_from_features(soup, wanted_label):
    try:
        for f in soup.select("div.adMainFeature"):
            label = f.select_one("p.adMainFeatureContentLabel")
            value = f.select_one("p.adMainFeatureContentValue")
            if label and value and wanted_label in label.get_text():
                return clean_text(value.get_text(" ", strip=True))
    except Exception:
        pass
    return None

def extract_rooms_baths(soup):
    chambres = None
    bains = None
    try:
        for f in soup.select("div.adDetailFeature"):
            if not chambres and f.select_one("i.icon-bed"):
                chambres = clean_text(f.get_text(" ", strip=True))
            if not bains and f.select_one("i.icon-bath"):
                bains = clean_text(f.get_text(" ", strip=True))
    except Exception:
        pass
    return chambres, bains

def extract_ville(soup, quartier, url):
    ville = None

    # 1) h4.titBlockProp ("Quartier à Ville")
    try:
        h4 = soup.select_one("h4.titBlockProp")
        if h4:
            txt_h4 = clean_text(h4.get_text(" ", strip=True))
            if txt_h4 and " à " in txt_h4:
                ville = txt_h4.split(" à ")[-1].strip()
    except Exception:
        pass

    # 2) depuis quartier "xxx à Casablanca"
    if not ville and quartier:
        q = clean_text(quartier)
        if q and " à " in q:
            ville = q.split(" à ")[-1].strip()

    # 3) features "Ville"
    if not ville:
        v = extract_from_features(soup, "Ville")
        if v:
            ville = v

    # 4) fallback URL
    if not ville and url:
        low = url.lower()
        for v in ["casablanca", "rabat", "marrakech", "tanger"]:
            if v in low:
                ville = v.capitalize()
                break

    ville = clean_text(ville)

    # normalisation
    if ville:
        norm = {"Casa": "Casablanca", "Tangier": "Tanger"}
        ville = norm.get(ville, ville)

    return ville

# =========================================================
# SCRAPER
# =========================================================
def scraping_location_all():
    global driver

    # 1) Charger ce qui est déjà scrapé
    locations = load_locations()

    # 2) Charger la progression
    prog = load_progress()
    page = 38

    # 3) Déduire compteur depuis data (pour ne pas réécrire annonce_1...)
    compteur_data = infer_compteur_from_data(locations)
    compteur = max(int(prog.get("compteur", 0)), compteur_data)

    print("\n" + "=" * 70)
    print("SCRAPING LOCATION (RESUME) — MUBAWAB")
    print("=" * 70)
    print("URL BASE:", URL_BASE)
    print(f"✅ Déjà scrapé: {len(locations)} annonces | compteur={compteur} | reprise page={page}")

    consecutive_timeouts = 0
    wait = WebDriverWait(driver, 15)

    try:
        while page <= MAX_PAGES and compteur < MAX_ANNONCES:
            print(f"\n{'-' * 70}")
            print(f"PAGE {page}/{MAX_PAGES}")
            print(f"{'-' * 70}")

            url_page = URL_BASE if page == 1 else (URL_BASE + f":p:{page}")
            print("URL:", url_page)

            if not safe_get(url_page):
                consecutive_timeouts += 1
                print("⛔ Page trop lente → on saute et on continue")
                if consecutive_timeouts >= 3:
                    print("🔄 Trop de pages lentes → restart navigateur")
                    restart_driver()
                    wait = WebDriverWait(driver, 15)
                    consecutive_timeouts = 0
                page += 1
                save_progress(page, compteur)
                continue
            else:
                consecutive_timeouts = 0

            time.sleep(2)

            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "listingBox")))
            except Exception:
                print("Aucune annonce détectée → on continue")
                page += 1
                save_progress(page, compteur)
                continue

            annonces = driver.find_elements(By.CLASS_NAME, "listingBox")
            print("Annonces sur la page:", len(annonces))

            if not annonces:
                page += 1
                save_progress(page, compteur)
                continue

            liens = []
            for a in annonces:
                l = a.get_attribute("linkref")
                if l and "/fr/a/" in l:
                    liens.append(l)

            print("Liens annonce valides:", len(liens))

            for lien in liens:
                if compteur >= MAX_ANNONCES:
                    print("🛑 LIMITE 5000 ATTEINTE")
                    break

                # ✅ éviter les doublons si on relance
                already = any(v.get("url") == lien for v in locations.values())
                if already:
                    continue

                compteur += 1
                print(f"[{compteur}] {lien}")

                if compteur % RESTART_EVERY == 0:
                    print("🧹 Nettoyage navigateur (restart)")
                    restart_driver()
                    wait = WebDriverWait(driver, 15)

                if not safe_get(lien):
                    print("⚠ Lien ignoré (trop lent)")
                    continue

                time.sleep(1.5)

                try:
                    html = driver.page_source
                except InvalidSessionIdException:
                    print("💥 Session perdue (page_source) → restart")
                    restart_driver()
                    wait = WebDriverWait(driver, 15)
                    continue
                except Exception:
                    print("⚠ page_source impossible → restart")
                    restart_driver()
                    wait = WebDriverWait(driver, 15)
                    continue

                soup = BeautifulSoup(html, "html.parser")

                prix = None
                hprix = soup.select_one("h3.orangeTit")
                if hprix:
                    prix = clean_text(hprix.get_text(" ", strip=True))

                surface = extract_surface(soup)

                quartier = None
                hq = soup.select_one("h3.greyTit")
                if hq:
                    quartier = clean_text(hq.get_text(" ", strip=True))

                type_bien = extract_type_bien(soup)
                chambres, bains = extract_rooms_baths(soup)

                date_annonce = None
                dd = soup.select_one("span.adDispDate")
                if dd:
                    date_annonce = clean_text(dd.get_text(" ", strip=True))

                ville = extract_ville(soup, quartier, lien)

                locations[f"annonce_{compteur}"] = {
                    "id": compteur,
                    "ville": ville,
                    "prix": prix,
                    "surface": surface,
                    "quartier": quartier,
                    "type_bien": type_bien,
                    "nb_chambres": chambres,
                    "nb_salle_de_bain": bains,
                    "date_annonce": date_annonce,
                    "url": lien
                }

                if compteur % BACKUP_EVERY == 0:
                    save_locations(locations, backup=True)
                    save_locations(locations, backup=False)
                    save_progress(page, compteur)
                    print("💾 Backup + progress sauvegardés")

            # fin page
            page += 1
            save_progress(page, compteur)

        # sauvegarde finale
        save_locations(locations, backup=False)
        save_locations(locations, backup=True)
        save_progress(page, compteur)

        print("\n✅ TERMINÉ")
        print("Total annonces:", len(locations))

    finally:
        try:
            driver.quit()
        except Exception:
            pass

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    scraping_location_all()