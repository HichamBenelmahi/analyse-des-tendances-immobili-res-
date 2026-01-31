from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import re
from bs4 import BeautifulSoup

URL = "https://www.mubawab.ma/"

# Configuration du navigateur
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get(URL)

ventes = {}

def scraping_complet():
    try:
        wait = WebDriverWait(driver, 15)
        
        # ========== ÉTAPE 1: FERMETURE POPUP ==========
        print("\n" + "="*70)
        print("ÉTAPE 1: FERMETURE POPUP")
        print("="*70)
        try:
            fermer_popup = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "fancybox-close")))
            fermer_popup.click()
            print("✓ Popup fermé")
            time.sleep(1)
        except:
            print("⚠ Pas de popup trouvé")
        
        # ========== ÉTAPE 2: CLIC SUR VENTE ==========
        print("\n" + "="*70)
        print("ÉTAPE 2: CLIC SUR VENTE")
        print("="*70)
        lien_vente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://www.mubawab.ma/fr/sc/appartements-a-vendre']")))
        lien_vente.click()
        print("✓ Clic sur Vente")
        time.sleep(3)
        
        # ========== ÉTAPE 3: SÉLECTION DES VILLES ==========
        print("\n" + "="*70)
        print("ÉTAPE 3: SÉLECTION DES VILLES")
        print("="*70)
        
        villes = ['Casablanca', 'Rabat', 'Marrakech', 'Tanger']
        
        location_container = wait.until(EC.element_to_be_clickable((By.ID, "locationInputContainer")))
        location_container.click()
        print("✓ Conteneur de localisation cliqué")
        time.sleep(2)
        
        for ville in villes:
            print(f"\n→ Sélection de {ville}...")
            
            search_box = wait.until(EC.visibility_of_element_located((By.ID, "filterCitySearchBoxInput")))
            search_box.clear()
            time.sleep(0.5)
            
            for char in ville:
                search_box.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(2)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "selectUl")))
            time.sleep(1)
            
            ville_cliquee = False
            try:
                ville_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@class='place' and @placetype='City']//label[contains(text(), '{ville}')]")
                ))
                driver.execute_script("arguments[0].click();", ville_option)
                ville_cliquee = True
                print(f"  ✓ {ville} sélectionnée")
            except:
                pass
            
            if not ville_cliquee:
                try:
                    premier_resultat = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "ul.selectUl li.level-0 div.place")
                    ))
                    driver.execute_script("arguments[0].click();", premier_resultat)
                    print(f"  ✓ {ville} sélectionnée (méthode alternative)")
                except:
                    print(f"  ✗ Impossible de sélectionner {ville}")
            
            time.sleep(1)
        
        print("\n✓ Toutes les villes sélectionnées!")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(2)
        
        # ========== ÉTAPE 4: SÉLECTION DES TYPES ==========
        print("\n" + "="*70)
        print("ÉTAPE 4: SÉLECTION DES TYPES DE BIENS")
        print("="*70)
        
        type_input = wait.until(EC.element_to_be_clickable((By.ID, "adTypeInput")))
        type_input.click()
        print("✓ Input des types cliqué")
        time.sleep(2)
        
        wait.until(EC.presence_of_element_located((By.ID, "adTypeOptions")))
        print("✓ Options visibles\n")
        
        # Récupérer tous les types disponibles
        type_buttons = driver.find_elements(By.CSS_SELECTOR, "#adTypeOptions button.adTypeItem")
        
        # Identifier tous les types sauf "land"
        types_a_activer = []
        for button in type_buttons:
            type_value = button.get_attribute("value")
            if type_value and "land" not in type_value.lower():
                types_a_activer.append(type_value)
        
        print(f"Types à activer: {len(types_a_activer)}\n")
        
        # Activer tous les types un par un
        types_selectionnes = 0
        for type_value in types_a_activer:
            try:
                button = driver.find_element(By.CSS_SELECTOR, f"button[value='{type_value}']")
                classes = button.get_attribute("class")
                is_active = "active" in classes if classes else False
                type_name = type_value.replace("-sale", "").replace("-", " ").title()
                
                if not is_active:
                    print(f"  → Activation de: {type_name}...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.8)
                    
                    updated_button = driver.find_element(By.CSS_SELECTOR, f"button[value='{type_value}']")
                    updated_classes = updated_button.get_attribute("class")
                    
                    if "active" in updated_classes:
                        print(f"    ✓ {type_name} activé")
                        types_selectionnes += 1
                    else:
                        print(f"    ✗ Échec activation {type_name}")
                else:
                    print(f"  ✓ {type_name} déjà actif")
                    types_selectionnes += 1
                    
            except Exception as e:
                print(f"  ✗ Erreur avec {type_value}: {e}")
        
        print(f"\n✓ Total: {types_selectionnes} types sélectionnés")
        time.sleep(1)
        
        try:
            type_input_value = driver.find_element(By.ID, "adTypeInput").get_attribute("value")
            print(f"✓ Valeur de l'input: '{type_input_value}'")
        except:
            print("⚠ Impossible de vérifier la valeur de l'input")
        
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(2)
        
        # ========== ÉTAPE 5: SCRAPING ==========
        print("\n" + "="*70)
        print("ÉTAPE 5: SCRAPING DES ANNONCES")
        print("="*70 + "\n")
        
        # Récupérer l'URL de base (celle avec tous les filtres)
        url_base = driver.current_url
        print(f"URL de base: {url_base}\n")
        
        compteur_global = 0
        page_actuelle = 1
        
        while True:
            print(f"\n{'─'*70}")
            print(f"PAGE {page_actuelle}")
            print(f"{'─'*70}\n")
            
            # Construire l'URL de la page
            if page_actuelle == 1:
                url_page = url_base
            else:
                # Ajouter :p:{numéro_page} à l'URL
                if ':p:' in url_base:
                    # Remplacer le numéro de page existant
                    url_page = re.sub(r':p:\d+', f':p:{page_actuelle}', url_base)
                else:
                    # Ajouter le numéro de page
                    url_page = url_base + f':p:{page_actuelle}'
            
            print(f"URL de la page: {url_page}")
            driver.get(url_page)
            time.sleep(3)
            
            # Attendre le chargement
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "listingBox")))
            except:
                print("Aucune annonce trouvée sur cette page - Fin")
                break
            
            time.sleep(2)
            
            # Récupérer les annonces
            liens = []
            annonces = driver.find_elements(By.CLASS_NAME, "listingBox")
            print(f"Nombre d'annonces sur la page: {len(annonces)}\n")
            
            if len(annonces) == 0:
                print("Aucune annonce trouvée - Fin de la pagination")
                break
            
            for annonce in annonces:
                lien = annonce.get_attribute("linkref")
                if lien:
                    liens.append(lien)
            
            print(f"{len(liens)} liens à traiter\n")
            
            # Traiter les annonces
            for idx, lien in enumerate(liens, 1):
                compteur_global += 1
                print(f"  [{compteur_global}] Annonce {idx}/{len(liens)}...")
                
                driver.get(lien)
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extraire le prix
                try:
                    prix_element = soup.find('h3', class_='orangeTit')
                    if prix_element:
                        prix = prix_element.get_text(strip=True)
                        prix = re.split(r'Baisse|Hausse', prix)[0].strip()
                    else:
                        prix = None
                except:
                    prix = None
                
                # Extraire la surface
                try:
                    surface = None
                    for feature in soup.find_all('div', class_='adDetailFeature'):
                        span = feature.find('span')
                        if span:
                            span_text = span.get_text(strip=True)
                            span_text = re.sub(r'\s+', ' ', span_text)
                            if 'm²' in span_text or 'm2' in span_text:
                                surface = span_text
                                break
                except:
                    surface = None
                
                # Extraire le quartier
                try:
                    quartier_element = soup.find('h3', class_='greyTit')
                    if quartier_element:
                        quartier_complet = quartier_element.get_text(strip=True)
                        if ' à ' in quartier_complet:
                            quartier = quartier_complet.split(' à ')[0].strip()
                        else:
                            quartier = quartier_complet
                    else:
                        quartier = None
                except:
                    quartier = None
                
                # Extraire la ville depuis 'titBlockProp inBlock'
                ville = None
                try:
                    # Méthode 1: Depuis le h4 dans titBlockProp inBlock
                    title_block = soup.find('h4', class_='titBlockProp inBlock')
                    if title_block:
                        title_text = title_block.get_text(strip=True)
                        # Format attendu: "Quartier à Ville"
                        if ' à ' in title_text:
                            ville = title_text.split(' à ')[-1].strip()
                        else:
                            # Sinon, chercher dans le texte
                            villes_possibles = ['Casablanca', 'Rabat', 'Marrakech', 'Tanger', 
                                              'Casa', 'Tangier', 'Tanja']
                            for v in villes_possibles:
                                if v.lower() in title_text.lower():
                                    # Normaliser le nom
                                    if v.lower() in ['casa']:
                                        ville = 'Casablanca'
                                    elif v.lower() in ['tanja', 'tangier']:
                                        ville = 'Tanger'
                                    else:
                                        ville = v.capitalize()
                                    break
                except:
                    pass
                
                # Si pas trouvée, essayer depuis blockProp mapBlockProp (la carte)
                if not ville:
                    try:
                        map_block = soup.find('div', class_='blockProp mapBlockProp')
                        if map_block:
                            h4 = map_block.find('h4', class_='titBlockProp inBlock')
                            if h4:
                                map_text = h4.get_text(strip=True)
                                if ' à ' in map_text:
                                    ville = map_text.split(' à ')[-1].strip()
                    except:
                        pass
                
                # Si toujours pas trouvée, chercher dans le quartier
                if not ville and quartier:
                    villes_possibles = ['Casablanca', 'Rabat', 'Marrakech', 'Tanger']
                    for v in villes_possibles:
                        if v.lower() in quartier.lower():
                            ville = v
                            break
                
                # Si toujours pas trouvée, chercher dans les features
                if not ville:
                    try:
                        for feature in soup.find_all('div', class_='adMainFeature'):
                            label = feature.find('p', class_='adMainFeatureContentLabel')
                            if label and 'Ville' in label.get_text():
                                value = feature.find('p', class_='adMainFeatureContentValue')
                                if value:
                                    ville = value.get_text(strip=True)
                                    break
                    except:
                        pass
                
                # Extraire le type de bien
                try:
                    type_bien = None
                    for feature in soup.find_all('div', class_='adMainFeature'):
                        label = feature.find('p', class_='adMainFeatureContentLabel')
                        if label and 'Type de bien' in label.get_text():
                            value = feature.find('p', class_='adMainFeatureContentValue')
                            if value:
                                type_bien = value.get_text(strip=True)
                                break
                except:
                    type_bien = None
                
                # Extraire le nombre de chambres
                try:
                    nb_chambres = None
                    for feature in soup.find_all('div', class_='adDetailFeature'):
                        icon = feature.find('i', class_='icon-bed')
                        if icon:
                            span = feature.find('span')
                            if span:
                                nb_chambres = span.get_text(strip=True)
                                break
                    
                    if not nb_chambres:
                        for feature in soup.find_all('div', class_='adDetailFeature'):
                            icon = feature.find('i', class_='icon-house-boxes')
                            if icon:
                                span = feature.find('span')
                                if span:
                                    nb_chambres = span.get_text(strip=True)
                                    break
                except:
                    nb_chambres = None
                
                # Extraire le nombre de salles de bain
                try:
                    nb_salle_de_bain = None
                    for feature in soup.find_all('div', class_='adDetailFeature'):
                        icon = feature.find('i', class_='icon-bath')
                        if icon:
                            span = feature.find('span')
                            if span:
                                nb_salle_de_bain = span.get_text(strip=True)
                                break
                except:
                    nb_salle_de_bain = None
                
                # Extraire la date d'annonce
                try:
                    date_annonce = soup.find('span', class_='adDispDate')
                    if date_annonce:
                        date_annonce = date_annonce.get_text(strip=True)
                    else:
                        date_annonce = None
                except:
                    date_annonce = None
                
                # Stocker les données
                annonce_id = f"annonce_{compteur_global}"
                ventes[annonce_id] = {
                    'id': annonce_id,
                    'ville': ville,
                    'prix': prix,
                    'surface': surface,
                    'quartier': quartier,
                    'type_bien': type_bien,
                    'nb_chambres': nb_chambres,
                    'nb_salle_de_bain': nb_salle_de_bain,
                    'url_annonce': lien,
                    'date_annonce': date_annonce
                }
                
                print(f"      ✓ {ville} | {type_bien} | {prix} | {surface}")
            
            print(f"\n✓ Page {page_actuelle} terminée: {len(liens)} annonces extraites")
            
            # Sauvegarder après chaque page
            with open('annonces_ventes_backup.json', 'w', encoding='utf-8') as f:
                json.dump(ventes, f, ensure_ascii=False, indent=4)
            print(f"  → Backup sauvegardé ({len(ventes)} annonces)")
            
            # Passer à la page suivante
            page_actuelle += 1
            
            # Vérifier s'il y a une page suivante en retournant à l'URL de base
            print(f"\n→ Vérification de la page {page_actuelle}...")
            time.sleep(2)
        
        # Sauvegarder le fichier final
        with open('annonces_ventes.json', 'w', encoding='utf-8') as f:
            json.dump(ventes, f, ensure_ascii=False, indent=4)
        
        print("\n" + "="*70)
        print("EXTRACTION TERMINÉE")
        print("="*70)
        print(f"Total de pages scrapées: {page_actuelle - 1}")
        print(f"Total d'annonces extraites: {len(ventes)}")
        print(f"Résultats sauvegardés dans: annonces_ventes.json")
        
        # ========== STATISTIQUES ==========
        print("\n" + "="*70)
        print("STATISTIQUES")
        print("="*70)
        
        villes_count = {}
        types_count = {}
        
        for annonce_id, details in ventes.items():
            ville = details.get('ville', 'Inconnue')
            type_bien = details.get('type_bien', 'Inconnu')
            
            villes_count[ville] = villes_count.get(ville, 0) + 1
            types_count[type_bien] = types_count.get(type_bien, 0) + 1
        
        print("\nAnnonces par ville:")
        for ville, count in sorted(villes_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ville}: {count} annonces")
        
        print("\nAnnonces par type:")
        for type_bien, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {type_bien}: {count} annonces")
    
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("erreur_scraping.png")
        
        if ventes:
            with open('annonces_ventes_erreur.json', 'w', encoding='utf-8') as f:
                json.dump(ventes, f, ensure_ascii=False, indent=4)
            print(f"\n⚠ Données partielles sauvegardées: {len(ventes)} annonces")
    
    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    scraping_complet()