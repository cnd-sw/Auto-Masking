import spacy
import re

class AutoMasker:
    def __init__(self, model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Model '{model}' not found. Please run: python -m spacy download {model}")
            self.nlp = None

    def mask_message(self, message: str) -> str:
        """
        Masks named entities and specific patterns in the message.
        """
        if not self.nlp:
            return "Error: Model not loaded."

        # 1. Pre-masking custom patterns (Hybrid approach)
        # Using specific regex for things standard NER might struggle with in local contexts,
        # or to ensure high precision for financial data.
        masked_message = message

        # Mask dates (DD-MM-YYYY, DD/MM/YYYY, etc)
        masked_message = re.sub(r'\d{2}[-/]\d{2}[-/]\d{2,4}', '<DATE>', masked_message)
        
        # Mask Currency Amounts (Rs 100, INR 500, Rs. 100.00)
        # We process this BEFORE Spacy because 'Rs 1000' shouldn't become a Date.
        # Handle decimal amounts too: 100.50
        masked_message = re.sub(r'(?i)(rs\.?|inr|rp\.?)\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', '<AMOUNT>', masked_message)
        
        # Mask digits that look like masked account numbers
        masked_message = re.sub(r'[X*x]{2,}\d{3,}', '<ACCOUNT>', masked_message)
        masked_message = re.sub(r'(?i)(account\s+no\.?\s*)(\d+)', r'\1<ACCOUNT>', masked_message)

        # 2. NLP-based masking
        doc = self.nlp(masked_message)
        
        new_text = masked_message
        
        # Spacy entities
        for ent in reversed(doc.ents):
            # print(f"Debug: Entity '{ent.text}' label '{ent.label_}'")
            if ent.label_ in ["MONEY", "CARDINAL", "DATE", "TIME", "ORG", "PERSON", "GPE"]:
                label_map = {
                    "MONEY": "<AMOUNT>",
                    "CARDINAL": "<NUMBER>",
                    "DATE": "<DATE>",
                    "TIME": "<TIME>",
                    "ORG": "<ENTITY>",
                    "PERSON": "<ENTITY>",
                    "GPE": "<LOCATION>"
                }
                
                if ent.label_ == "DATE" and ent.text.isdigit():
                    # Spacy often mistakes 4 or 6 digit numbers as years or dates. 
                    # If it's pure digits, treat as NUMBER.
                    tag = "<NUMBER>"
                else:
                    tag = label_map.get(ent.label_, f"<{ent.label_}>")
                
                start = ent.start_char
                end = ent.end_char
                
                current_slice = new_text[start:end]
                # Avoid destroying our existing tags
                if "<" not in current_slice:
                     new_text = new_text[:start] + tag + new_text[end:]
        
        # 3. Post-processing cleanup
        
        return new_text

if __name__ == "__main__":
    masker = AutoMasker()
    if masker.nlp:
        sample = "You have paid Rs 100 to Swiggy and your balance is Rs 1000 on 12-05-2025."
        print(f"Original: {sample}")
        print(f"Masked:   {masker.mask_message(sample)}")
