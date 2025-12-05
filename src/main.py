import hashlib
from masker import AutoMasker

def generate_template_hash(template_str: str) -> str:
    """Generate a consistent hash for a template string."""
    # Normalize whitespace before hashing
    clean_template = " ".join(template_str.split())
    return hashlib.md5(clean_template.encode('utf-8')).hexdigest()

def main():
    masker = AutoMasker()
    if not masker.nlp:
        print("Failed to load NLP model.")
        return

    input_file = "data/input.txt"
    templates = {}

    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        return

    print(f"Processing {len(lines)} messages...\n")

    for line in lines:
        original = line.strip()
        if not original:
            continue
            
        masked = masker.mask_message(original)
        
        # Simple clustering by template hash
        tmpl_hash = generate_template_hash(masked)
        
        if tmpl_hash not in templates:
            templates[tmpl_hash] = {
                "template": masked,
                "count": 0,
                "examples": []
            }
        
        templates[tmpl_hash]["count"] += 1
        if len(templates[tmpl_hash]["examples"]) < 3:
            templates[tmpl_hash]["examples"].append(original)

    # Output results
    print("-" * 60)
    print(f"Found {len(templates)} unique templates:")
    print("-" * 60)
    
    for tmpl_hash, data in templates.items():
        print(f"Template: {data['template']}")
        print(f"Count:    {data['count']}")
        print("Examples:")
        for ex in data['examples']:
            print(f"  - {ex}")
        print("-" * 60)

if __name__ == "__main__":
    main()
