import time
import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# --- CONFIGURATION ---
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, "..", "data", "raw", "avito_vendre.csv")
os.makedirs(os.path.dirname(target_path), exist_ok=True)

# Colonnes demandées
COLUMNS = ["id", "ville", "prix", "surface", "quartier", "type_bien", "nb_chambres", "nb_salle_de_bains", "url_annonce", "date_annonce"]

if not os.path.exists(target_path):
    pd.DataFrame(columns=COLUMNS).to_csv(target_path, index=False, encoding='utf-8-sig')

def init_driver():
    ua = UserAgent()
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={ua.random}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.page_load_strategy = 'eager'
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_details(driver, url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    
    # Initialisation avec des valeurs par défaut (0 ou N/A)
    details = {
        "id": "null", "ville": "null", "prix": "null", "surface": "null", 
        "quartier": "null", "type_bien": "null", "nb_chambres": 0, 
        "nb_salle_de_bains": 0, "url_annonce": url, "date_annonce": "null"
    }

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # 1. Extraction de l'ID depuis l'URL (ex: ...57103649.htm -> 57103649)
        match_id = re.search(r'(\d+)\.htm', url)
        if match_id: details["id"] = match_id.group(1)

        # 2. TYPE DE BIEN (via Titre)
        titre_text = driver.find_element(By.TAG_NAME, "h1").text
        t_low = titre_text.lower()
        if "appartement" in t_low or "studio" in t_low: details["type_bien"] = "Appartement"
        elif "villa" in t_low or "riad" in t_low: details["type_bien"] = "Villa"
        elif "maison" in t_low: details["type_bien"] = "Maison"
        elif "terrain" in t_low: details["type_bien"] = "Terrain"
        elif "magasin" in t_low or "local" in t_low: details["type_bien"] = "Commerce"
        elif "bureau" in t_low: details["type_bien"] = "Bureau"

        page_text = driver.find_element(By.TAG_NAME, "body").text
        page_text_lower = page_text.lower()
        # 3. PRIX & SURFACE (Nettoyage numérique)        
        try:
            price_match = re.search(r'(\d[\d\s]+)\s*DH', page_text)
            if price_match:
                clean_price = re.sub(r"[^\d]", "", price_match.group(1))
                details["prix"] = f"{clean_price} DH"
        except: pass


        surface_keywords = ["surface totale", "m²", "m2", "surface"]
        
        for key in surface_keywords:
            # Cas 1 : Le nombre est AVANT le mot (ex: 10000 Surface totale - comme sur votre image)
            # On utilise \d+ pour les nombres entiers
            match = re.search(rf'(\d+)\s*{key}', page_text_lower)
            
            # Cas 2 : Le mot est AVANT le nombre (ex: Surface: 100)
            if not match:
                match = re.search(rf'{key}[:\s]*(\d+)', page_text_lower)
            
            if match:
                details["surface"] = f"{match.group(1)} m2"
                break # 

        # 4. NB_CHAMBRES (Somme : Chambres + Salons)
        nb_ch = 0
        nb_sa = 0
        ch_match = re.search(r'(\d+)\s*chambres?', page_text_lower)
        if ch_match: nb_ch = int(ch_match.group(1))
        sa_match = re.search(r'(\d+)\s*salons?', page_text_lower)
        if sa_match: nb_sa = int(sa_match.group(1))
        details["nb_chambres"] = nb_ch + nb_sa

        # 5. SALLE DE BAINS
        bain_match = re.search(r'(\d+)\s*salle\s*de\s*bain', page_text)
        if bain_match: details["nb_salle_de_bains"] = bain_match.group(1)

        # 6. DATE
        try: details["date_annonce"] = driver.find_element(By.TAG_NAME, 'time').text
        except: pass

        # 7. VILLE & QUARTIER
# --- EXTRACTION VILLE & QUARTIER VIA FIL D'ARIANE (BREADCRUMB) ---
        try:
            # On cherche la liste ordonnée (ol) qui contient les liens de navigation
            breadcrumb_items = driver.find_elements(By.XPATH, "//ol/li")
            
            if len(breadcrumb_items) >= 4:
                # Index 2 est toujours la Ville (ex: Casablanca)
                details["ville"] = breadcrumb_items[2].text.strip()
                
                # Index 3 est le Quartier (ex: Sidi Maarouf)
                # On vérifie que ce n'est pas déjà un mot technique comme "Avito Immobilier"
                quartier_candidat = breadcrumb_items[3].text.strip()
                if "Avito" not in quartier_candidat:
                    details["quartier"] = quartier_candidat
                else:
                    details["quartier"] = "N/A"
            
            elif len(breadcrumb_items) == 3:
                # Si la liste est plus courte, on ne prend que la ville
                details["ville"] = breadcrumb_items[2].text.strip()
                details["quartier"] = "N/A"
        
        except Exception as e:
            # Fallback : Si le fil d'ariane échoue, on tente de chercher le texte "Location"
            try:
                loc_element = driver.find_element(By.XPATH, "//span[contains(@class, 'Location')] | //p[contains(@class, 'Location')]")
                loc_text = loc_element.text
                if "," in loc_text:
                    parts = loc_text.split(",")
                    details["ville"] = parts[0].strip()
                    details["quartier"] = parts[1].strip()
                else:
                    details["ville"] = loc_text.strip()
            except: pass

    except Exception as e:
        print(f"Erreur extraction sur l'ID {details['id']}: {e}")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return details

# --- BOUCLE PRINCIPALE ---
driver = init_driver()
START_PAGE = 1 

try:
    for page in range(START_PAGE, 120):

        print(f"\n--- SCRAPING PAGE {page} ---")
        
        if page > START_PAGE and page % 20 == 0:
            driver.quit()
            driver = init_driver()
        BASE_URL = (
            "https://www.avito.ma/fr/maroc/villas_riad-%C3%A0_vendre"
            "?cities=8,15,5,12&has_price=true"
)
        driver.get(f"{BASE_URL}&o={page}")
        time.sleep(4)

        try:
            links_elems = driver.find_elements(By.XPATH, "//a[contains(@href, '.htm')]")
            urls = []
            for l in links_elems:
                href = l.get_attribute('href')
                if href and "/fr/" in href and href.count('/') >= 6:
                    if href not in urls: urls.append(href)
            
            page_data = []
            for url in urls:
                print(f"ID {url.split('-')[-1].replace('.htm','')} en cours...")
                info = get_details(driver, url)
                if info["id"] != "N/A":
                    page_data.append(info)
                time.sleep(1)

            if page_data:
                pd.DataFrame(page_data).to_csv(target_path, mode='a', header=False, index=False, encoding='utf-8-sig')

        except Exception as e:
            print(f"Erreur page {page}: {e}")
            continue

finally:
    driver.quit()
    print("Scraping terminé avec succès.")