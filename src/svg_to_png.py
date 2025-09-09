# bulk_convert_svg.py
import cairosvg
from pathlib import Path

# Assuming your SVGs are in a 'svg_assets' folder
INPUT_DIR = Path("./svg_assets")
# And you want to save the PNGs to your existing 'glyph' folder
OUTPUT_DIR = Path("./glyph")


def convert_svg_to_png():
    """Converts all SVG files in the input directory to PNG."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Iterate through all files in the input directory that end with .svg
    for svg_path in INPUT_DIR.glob("*.svg"):
        png_path = OUTPUT_DIR / f"{svg_path.stem}.png"

        print(f"Converting {svg_path.name} to PNG...")

        try:
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))
            print(f"✓ Success: {png_path.name}")
        except Exception as e:
            print(f"✗ Failed to convert {svg_path.name}: {e}")


if __name__ == "__main__":
    convert_svg_to_png()
