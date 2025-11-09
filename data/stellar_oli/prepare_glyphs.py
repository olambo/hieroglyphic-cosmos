import os
import lxml.etree as ET
import cairosvg

# Define the input and output directories
input_dir = './'
output_dir = '../stellar_pngs'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each SVG file
for filename in os.listdir(input_dir):
    if filename.endswith('.svg'):
        file_path = os.path.join(input_dir, filename)
        print(f"Processing {file_path}...")

        try:
            # Step 1: Parse the SVG file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Step 2: Remove the background <rect> element
            for rect in root.findall('.//{http://www.w3.org/2000/svg}rect', root.nsmap):
                rect.getparent().remove(rect)

            # Step 3: Change color by checking multiple attributes and elements
            all_elements = root.findall('.//*')
            for element in all_elements:
                style_attr = element.get('style')
                if style_attr:
                    new_style = style_attr.replace('fill:#000000', 'fill:white').replace('stroke:#000000', 'stroke:none')
                    element.set('style', new_style)
                
                if element.get('fill') is not None:
                    element.set('fill', 'white')
                if element.get('stroke') is not None:
                    element.set('stroke', 'none')

            # Step 4: Convert the modified SVG to PNG with a smaller fixed width
            cleaned_svg_data = ET.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

            png_filename = filename.replace('.svg', '.png')
            output_path = os.path.join(output_dir, png_filename)

            cairosvg.svg2png(
                bytestring=cleaned_svg_data,
                write_to=output_path,
                output_width=480,  # A smaller, more appropriate size
            )
            
            print(f"✅ Converted {filename} to {png_filename}")

        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")

print("\nAll files processed.")
