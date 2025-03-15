import csv
import re

def generate_anki_flashcards(sentences, base_name):
    """Generates an Anki-compatible CSV file for vocabulary words."""
    anki_data = []
    
    for chinese, english in sentences:
        # Extract vocabulary words (inside [][] brackets)
        vocab_matches = re.findall(r"\[(.*?)\]\[(.*?)\]", chinese)
        
        for vocab, meaning in vocab_matches:
            # Remove formatting from Chinese sentence
            chinese_clean = re.sub(r"\[(.*?)\]\[(.*?)\]", r"\1", chinese)
            chinese_clean = re.sub(r"\\p", "", chinese_clean)
            
            # Add to list as a row (word, full Chinese sentence, meaning, full English sentence)
            anki_data.append([vocab, chinese_clean, meaning, english])
    
    # Write to CSV
    csv_filename = f"{base_name}_anki.csv"
    with open(csv_filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["zh_vocab", "zh_sentence", "en_vocab", "en_sentence"])  # Header row
        writer.writerows(anki_data)
    
    print(f"Generated: {csv_filename}")