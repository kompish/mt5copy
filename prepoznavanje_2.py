import cv2
import numpy as np
import os

def find_currency_pair(image_path, templates_dir='pairs', threshold=0.8):
    """
    Pronalazi valutni par upoređivanjem sa poznatim šablonima.
    
    :param image_path: Putanja do ulazne slike
    :param templates_dir: Folder sa šablonima
    :param threshold: Prag podudarnosti (0-1)
    :return: Naziv valutnog para (npr. "EUR/USD") ili None
    """
    # Učitaj ulaznu sliku
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Ne mogu da učitam sliku: {image_path}")
    
    best_match = None
    max_val = 0
    
    # Prođi kroz sve šablone
    for template_file in os.listdir(templates_dir):
        if not template_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        
        # Učitaj šablon
        template_path = os.path.join(templates_dir, template_file)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
        
        # Izvrši template matching
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val_temp, _, _ = cv2.minMaxLoc(res)
        
        # Ažuriraj najbolji rezultat
        if max_val_temp > max_val and max_val_temp > threshold:
            max_val = max_val_temp
            best_match = os.path.splitext(template_file)[0].upper()
    
    return best_match.replace('_', '') if best_match else None

# Primer upotrebe
if __name__ == "__main__":
    result = find_currency_pair("media/photo_2025-05-15_11-22-34.jpg")
    print(f"Pronađen valutni par: {result}" if result else "Nije pronađen podudaran valutni par")