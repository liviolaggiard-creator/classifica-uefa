import os
import json
import re
import urllib.parse
import requests

def to_slug(team_name):
    """
    Converte il nome della squadra nello stesso formato 'slug'
    utilizzato dallo script JavaScript del sito.
    Esempio: 'Real Madrid CF' -> 'real-madrid-cf'
    """
    slug = team_name.lower()
    slug = re.sub(r'[^a-z0-9]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def get_wikimedia_logo_url(team_name):
    """
    Cerca su Wikimedia Commons il logo o stemma della squadra.
    """
    headers = {
        'User-Agent': 'UEFA-Ranking-App/1.0 (contact@example.com)'
    }
    
    # Query di ricerca prioritarie
    queries = [
        f"{team_name} logo png",
        f"{team_name} crest png",
        f"{team_name} badge png"
    ]
    
    for query in queries:
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6", # File namespace
            "gsrlimit": "5",
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "format": "json"
        }
        
        try:
            res = requests.get(search_url, params=params, headers=headers, timeout=5)
            data = res.json()
            
            if "query" in data and "pages" in data["query"]:
                pages = data["query"]["pages"]
                for page_id, page_data in pages.items():
                    image_info = page_data.get("imageinfo", [{}])[0]
                    mime = image_info.get("mime", "")
                    image_url = image_info.get("url", "")
                    
                    # Accetta solo PNG o SVG/WEBP convertibili
                    if "png" in mime or image_url.lower().endswith(".png"):
                        return image_url
        except Exception:
            continue
            
    return None

def download_logos():
    json_path = 'classifica.json'
    logos_dir = 'logos'
    
    if not os.path.exists(json_path):
        print(f"❌ Errore: File '{json_path}' non trovato nella cartella corrente.")
        return
        
    os.makedirs(logos_dir, exist_ok=True)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        teams = json.load(f)
        
    print(f"🔍 Trovate {len(teams)} squadre in {json_path}.\nStarting download...\n")
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for item in teams:
        team_name = item.get('team', '')
        if not team_name:
            continue
            
        slug = to_slug(team_name)
        file_path = os.path.join(logos_dir, f"{slug}.png")
        
        # Salta se l'immagine esiste già
        if os.path.exists(file_path):
            print(f"⏩ [GIA' PRESENTE] {team_name} -> {slug}.png")
            skipped += 1
            continue
            
        logo_url = get_wikimedia_logo_url(team_name)
        
        if logo_url:
            try:
                img_res = requests.get(logo_url, headers=headers, timeout=10)
                if img_res.status_code == 200:
                    with open(file_path, 'wb') as img_file:
                        img_file.write(img_res.content)
                    print(f"✅ [SCARICATO] {team_name} -> {slug}.png")
                    downloaded += 1
                else:
                    print(f"❌ [FALLITO] Impossibile scaricare l'immagine per: {team_name}")
                    failed += 1
            except Exception as e:
                print(f"❌ [ERRORE] Per {team_name}: {e}")
                failed += 1
        else:
            print(f"⚠️ [NON TROVATO] Nessun logo trovato per: {team_name}")
            failed += 1

    print("\n" + "="*40)
    print(f"📊 RIEPILOGO:")
    print(f"   - Scaricati con successo: {downloaded}")
    print(f"   - Già presenti: {skipped}")
    print(f"   - Non trovati/Falliti: {failed}")
    print("="*40)

if __name__ == "__main__":
    download_logos()