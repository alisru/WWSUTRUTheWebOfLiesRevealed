import os
import glob
import re
from bs4 import BeautifulSoup, NavigableString

def hyperlink_citations_in_files():
    """
    Finds all HTML files in the directory tree, identifies in-text citations 
    (e.g., [12], .12, or [4,11]), and hyperlinks them to the corresponding 
    entries in the "Works Cited" list. It uses a programmatic check to avoid 
    matching currency values.
    """
    print("Starting citation hyperlinking process...")
    html_files = glob.glob('**/*.html', recursive=True)
    
    files_to_exclude = [
        os.path.basename(__file__),
        'search.html',
    ]

    for filepath in html_files:
        if os.path.basename(filepath) in files_to_exclude:
            print(f" -> Skipping excluded file: {filepath}")
            continue

        print(f" -> Processing: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            parser = 'html.parser'
            soup = BeautifulSoup(content, parser)
            print("    - File parsed successfully.")
            
            # --- Step 1: Find and ID the citations in the "Works Cited" list ---
            # NEW ROBUST METHOD: First, try to find the section by its ID.
            works_cited_header = soup.find(id='works-cited')
            
            # If not found by ID, fall back to searching heading text content.
            if not works_cited_header:
                works_cited_header = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], string=re.compile(r'Works.Cited', re.IGNORECASE))

            if not works_cited_header:
                print("    - No 'Works Cited' section found by ID or text. Skipping.")
                continue

            citation_list = works_cited_header.find_next_sibling('ol')
            if not citation_list:
                print("    - No <ol> list found after 'Works Cited'. Skipping.")
                continue

            citations = citation_list.find_all('li')
            citation_count = len(citations)
            if citation_count == 0:
                print("    - 'Works Cited' list is empty. Skipping.")
                continue
            
            for i, li in enumerate(citations):
                li['id'] = f'citation-{i + 1}'
            
            print(f"    - Found {citation_count} citations to link.")

            # --- Step 2: Directly manipulate text nodes to insert hyperlinks ---
            main_content_area = soup.find('div', class_='markdown-body')
            if not main_content_area:
                print("    - Could not find main content area '.markdown-body'. Skipping.")
                continue
            
            citation_regex = re.compile(r'(\[[\d,\s]+\])|(\.\d{1,3}\b)')
            
            text_nodes = main_content_area.find_all(string=True, recursive=True)
            
            links_added = 0
            for node in text_nodes:
                if node.find_parent('ol') == citation_list or node.find_parent('a'):
                    continue

                original_text = str(node)
                all_matches = list(citation_regex.finditer(original_text))

                # --- Filter out matches that are likely currency ---
                valid_matches = []
                for match in all_matches:
                    full_match_text = match.group(0)
                    if full_match_text.startswith('.'):
                        start_index = match.start()
                        preceding_chunk = original_text[max(0, start_index - 10):start_index]
                        if '$' in preceding_chunk:
                            continue
                    valid_matches.append(match)

                if not valid_matches:
                    continue

                new_elements = []
                last_index = 0

                for match in valid_matches:
                    start, end = match.span()
                    
                    if start > last_index:
                        new_elements.append(NavigableString(original_text[last_index:start]))

                    full_match_text = match.group(0)
                    
                    if full_match_text.startswith('['): # Handle [n,n,...] format
                        content_inside = full_match_text[1:-1]
                        numbers_str = re.split(r',\s*', content_inside)
                        
                        new_elements.append(NavigableString('['))
                        for i, num_str in enumerate(numbers_str):
                            if num_str.isdigit():
                                num_int = int(num_str)
                                if 1 <= num_int <= citation_count:
                                    link = soup.new_tag('a', href=f'#citation-{num_int}')
                                    link.string = num_str
                                    new_elements.append(link)
                                    links_added += 1
                                else:
                                    new_elements.append(NavigableString(num_str))
                            else:
                                new_elements.append(NavigableString(num_str))
                            
                            if i < len(numbers_str) - 1:
                                new_elements.append(NavigableString(','))
                        new_elements.append(NavigableString(']'))

                    elif full_match_text.startswith('.'): # Handle .n format
                        num_str = full_match_text[1:]
                        num_int = int(num_str)
                        if 1 <= num_int <= citation_count:
                            link = soup.new_tag('a', href=f'#citation-{num_int}')
                            link.string = full_match_text
                            new_elements.append(link)
                            links_added += 1
                        else:
                            new_elements.append(NavigableString(full_match_text))
                    
                    last_index = end

                if last_index < len(original_text):
                    new_elements.append(NavigableString(original_text[last_index:]))
                
                if new_elements:
                    node.replace_with(*new_elements)

            # --- Step 3: Save the modified file ---
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"    - Success. Added {links_added} citation hyperlinks.")

        except Exception as e:
            print(f" -> ERROR processing file {filepath}: {e}")

    print("\nBatch citation hyperlinking complete!")


if __name__ == '__main__':
    hyperlink_citations_in_files()

