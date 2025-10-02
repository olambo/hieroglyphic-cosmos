# ### 1. Initial Diagnosis: File Size and Complexity

# Initially, we suspected the issue was related to **file size or complexity**. I provided you with commands to clean and optimize the files.

# * **`svg-cleaner` and `svgo`**: These tools were meant to remove unnecessary data and optimize the SVG code.
# * **`sed` commands**: I then suggested `sed` to strip XML declarations that can sometimes cause parsing issues. This attempt unfortunately led to the files being emptied due to an issue with the command's syntax.

# ---

# ### 2. Correct Diagnosis: Application vs. Environment

# The key turning point was when you provided the **Inkscape crash log**. This showed that the crash was happening during the application's startup, not when a specific file was opened. This led us to the correct diagnosis: the problem was an **application-level issue or a conflict with your system's Python environment**, not the SVG files themselves.

# * **Virtual Environment Issue**: We discovered that the `lxml` library, which was needed to process the files, was installed in a virtual environment that your script wasn't using.
# * **Corrupted Environment**: The virtual environment itself was likely corrupted, which we confirmed by the persistent `ModuleNotFoundError`.

# ---

# ### 3. The Final Solution

# We resolved the issue by taking a step back and creating a **clean, reliable environment** to work from.

# 1.  **Environment Reset**: We deleted your existing virtual environment and created a new one from scratch. This provided a clean slate.
# 2.  **Safe Python Script**: I provided a **Python script** that was a more reliable and surgical way to clean the SVG files. It used the `lxml` library to correctly parse and remove specific, problematic metadata that was likely causing the crash.
# 3.  **Execution**: You then ran the script in the correct environment, and it successfully cleaned the files without any errors.

# In the end, the solution wasn't to "fix" Inkscape itself, but to provide it with **cleaner, more compatible files** by using a robust and safe scripting approach to process them.

# ### 1. Initial Diagnosis: File Size and Complexity

# Initially, we suspected the issue was related to **file size or complexity**. I provided you with commands to clean and optimize the files.

# * **`svg-cleaner` and `svgo`**: These tools were meant to remove unnecessary data and optimize the SVG code.
# * **`sed` commands**: I then suggested `sed` to strip XML declarations that can sometimes cause parsing issues. This attempt unfortunately led to the files being emptied due to an issue with the command's syntax.

# ---

# ### 2. Correct Diagnosis: Application vs. Environment

# The key turning point was when you provided the **Inkscape crash log**. This showed that the crash was happening during the application's startup, not when a specific file was opened. This led us to the correct diagnosis: the problem was an **application-level issue or a conflict with your system's Python environment**, not the SVG files themselves.

# * **Virtual Environment Issue**: We discovered that the `lxml` library, which was needed to process the files, was installed in a virtual environment that your script wasn't using.
# * **Corrupted Environment**: The virtual environment itself was likely corrupted, which we confirmed by the persistent `ModuleNotFoundError`.

# ---

# ### 3. The Final Solution

# We resolved the issue by taking a step back and creating a **clean, reliable environment** to work from.

# 1.  **Environment Reset**: We deleted your existing virtual environment and created a new one from scratch. This provided a clean slate.
# 2.  **Safe Python Script**: I provided a **Python script** that was a more reliable and surgical way to clean the SVG files. It used the `lxml` library to correctly parse and remove specific, problematic metadata that was likely causing the crash.
# 3.  **Execution**: You then ran the script in the correct environment, and it successfully cleaned the files without any errors.

# In the end, the solution wasn't to "fix" Inkscape itself, but to provide it with **cleaner, more compatible files** by using a robust and safe scripting approach to process them.
import os
import lxml.etree as ET

# Define the root directory where your SVG files are located
svg_root_dir = './'

print(f"Starting recursive cleanup from: {svg_root_dir}")

# os.walk iterates through all subdirectories
for root, dirs, files in os.walk(svg_root_dir):
    for filename in files:
        if filename.endswith('.svg'):
            file_path = os.path.join(root, filename)
            
            # Skip the script itself if it happens to be named .svg (unlikely, but safe)
            if file_path == './clean_svgs.py':
                continue

            # print(f"Processing {file_path}...") # You can uncomment this to see every file

            try:
                # Parse the SVG file as XML
                tree = ET.parse(file_path)
                root_element = tree.getroot()

                # 1. Remove all 'metadata' elements
                for element in root_element.findall('.//{http://www.w3.org/2000/svg}metadata', root_element.nsmap):
                    element.getparent().remove(element)
                
                # 2. Remove all 'sodipodi:namedview' elements
                ns = {'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'}
                for element in root_element.findall('.//sodipodi:namedview', ns):
                    element.getparent().remove(element)
                
                # Save the cleaned XML back to the same file
                tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
                
                print(f"Successfully cleaned: {file_path}")

            except Exception as e:
                print(f"FAILED to process {file_path}: {e}")

print("\nAll directories processed.")
