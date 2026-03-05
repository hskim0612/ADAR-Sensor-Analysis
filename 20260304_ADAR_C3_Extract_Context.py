import textwrap

def extract_context(fasta_path, sites, window=150):
    with open(fasta_path, 'r') as f:
        lines = f.readlines()
        seq = "".join([line.strip() for line in lines if not line.startswith('>')]).upper()
    
    results = {}
    for site in sites:
        start = max(0, site - window)
        end = min(len(seq), site + window)
        context = seq[start:end]
        results[site] = context
        print(f"Site {site}: Context Length {len(context)}")
        
    return results

if __name__ == "__main__":
    fasta_file = "human_C3_mRNA.fasta"
    target_sites = [1623, 1131, 297, 2704, 3436, 2688]
    contexts = extract_context(fasta_file, target_sites)
    
    with open("c3_multi_site_contexts.json", "w") as jf:
        import json
        json.dump(contexts, jf, indent=4)
    print("Context extraction complete. Data saved to c3_multi_site_contexts.json")
