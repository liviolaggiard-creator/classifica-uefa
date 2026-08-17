import os
import re

logos_dir = 'logos'

for filename in os.listdir(logos_dir):
    if filename.endswith('.png') and '-' in filename:
        # Rimuove la prima parola prima del primo trattino (la nazione)
        parts = filename.split('-', 1)
        if len(parts) > 1:
            new_filename = parts[1]
            old_path = os.path.join(logos_dir, filename)
            new_path = os.path.join(logos_dir, new_filename)
            
            os.rename(old_path, new_path)
            print(f"Rinominato: {filename} -> {new_filename}")