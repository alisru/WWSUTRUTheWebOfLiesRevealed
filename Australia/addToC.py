import os
import glob
import re

# --- 1. Define the HTML and JavaScript to be injected ---

toc_html_to_add = """
    <!-- TOC Drawer for both desktop and mobile -->
    <nav id="toc-container"></nav>

    <!-- Mobile-only header with toggle button -->
    <header id="mobile-header">
        <button id="toc-toggle-btn">
            <span></span>
            <span></span>
            <span></span>
        </button>
    </header>

    <!-- Overlay for mobile drawer -->
    <div id="toc-overlay"></div>
"""

toc_script_to_add = """
<script>
document.addEventListener('DOMContentLoaded', function () {
    // --- 1. Element Selection ---
    const tocContainer = document.getElementById('toc-container');
    const contentContainer = document.querySelector('.markdown-body');
    const tocToggleButton = document.getElementById('toc-toggle-btn');
    const tocOverlay = document.getElementById('toc-overlay');

    if (!tocContainer || !contentContainer) return;

    // --- 2. Generate TOC Content ---
    const headings = contentContainer.querySelectorAll('h2, h3');
    if (headings.length === 0) {
        tocContainer.style.display = 'none';
        if (tocToggleButton) tocToggleButton.style.display = 'none';
        return;
    }

    const tocTitle = document.createElement('h4');
    tocTitle.textContent = 'On this page';
    tocContainer.appendChild(tocTitle);
    const tocList = document.createElement('ul');

    headings.forEach((heading, index) => {
        if (!heading.id) heading.id = `heading-ref-${index}`;
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.textContent = heading.textContent;
        link.href = `#${heading.id}`;
        link.classList.add(heading.tagName.toLowerCase() === 'h3' ? 'toc-h3' : 'toc-h2');
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });
    tocContainer.appendChild(tocList);
    const tocLinks = tocContainer.querySelectorAll('a');

    // --- 3. Mobile Drawer Functionality ---
    const closeTocDrawer = () => document.body.classList.remove('toc-open');
    if (tocToggleButton && tocOverlay) {
        tocToggleButton.addEventListener('click', () => document.body.classList.toggle('toc-open'));
        tocOverlay.addEventListener('click', closeTocDrawer);
    }
    tocLinks.forEach(link => link.addEventListener('click', closeTocDrawer));

    // --- 4. Active Link Highlighting on Scroll ---
    const getAbsoluteTop = (element) => {
        let top = 0;
        while (element) {
            top += element.offsetTop;
            element = element.offsetParent;
        }
        return top;
    };
    
    const headingPositions = Array.from(headings).map(h => ({
        id: h.id,
        top: getAbsoluteTop(h)
    }));
    
    let scrollTimeout;
    const setActiveLink = () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            let currentId = '';
            const scrollPosition = window.scrollY + 120; // Offset for better UX

            for (let i = headingPositions.length - 1; i >= 0; i--) {
                if (scrollPosition >= headingPositions[i].top) {
                    currentId = headingPositions[i].id;
                    break;
                }
            }

            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${currentId}`) {
                    link.classList.add('active');
                }
            });
        }, 50); // 50ms debounce delay
    };

    window.addEventListener('scroll', setActiveLink);
    setActiveLink(); // Set initial state
});
</script>
"""

# --- 2. Find and update all HTML files ---

# This will find every .html file in the current directory and all subdirectories.
html_files = glob.glob('**/*.html', recursive=True)

for filepath in html_files:
    if os.path.basename(filepath) == os.path.basename(__file__):
        continue # Don't process the script itself

    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if the TOC has already been added to avoid duplicates
        if 'id="toc-container"' in content:
            print(" -> Already contains TOC. Skipping.")
            continue

        original_content = content
        
        # Use a regular expression to find the opening body tag, case-insensitively,
        # and handle any attributes it might have (like class or id).
        # The re.sub() function replaces only the first occurrence (count=1).
        content = re.sub(r'<body.*?>', lambda m: m.group(0) + toc_html_to_add, content, count=1, flags=re.IGNORECASE | re.DOTALL)

        # Use a regular expression to find the closing body tag, case-insensitively,
        # and insert the script before it.
        content = re.sub(r'</body>', toc_script_to_add + '\n</body>', content, count=1, flags=re.IGNORECASE)

        # Only write to the file if a change was actually made.
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f" -> Successfully Updated.")
        else:
            print(" -> No <body> tag found. Skipped update.")

    except Exception as e:
        print(f" -> ERROR processing file: {e}")

print("\nBatch update complete!")

