# AI Development Partners:
#   - Claude (Anthropic): Code adaptation from Cygni Arcana, coordinate system preservation,
#     Egyptian astronomical research integration, and hieroglyphic mapping framework
#   - Previous Cygni Arcana contributors: Grok (xAI), ChatGPT (OpenAI), Gemini (Google)
#
# This project represents the evolution from tarot-stellar mapping to historically-grounded
# Egyptian hieroglyphic-stellar connections, maintaining astronomical precision while
# embracing authentic ancient Egyptian cosmic symbolism.
#
# *** COORDINATE DATA WARNING ***
# STELLAR COORDINATES ARE ROUGH ESTIMATES - MUST BE VERIFIED WITH SIMBAD QUERIES
# Current coordinates are approximations for layout testing only.
# For publication quality: Query SIMBAD directly for precise RA/Dec coordinates,
# then convert to galactic coordinates using standard transformations.
# 33 stars require SIMBAD verification before final publication.
#
# DATA SOURCES & COORDINATE SYSTEM:
# - Star positions: [TO BE VERIFIED] SIMBAD, Gaia DR3, Hipparcos Catalogue
# - Egyptian stellar references: Neugebauer & Parker, Lull & Belmonte, ancient star maps
# - Hieroglyphic sources: Gardiner sign list, Budge hieroglyphic dictionary
# - Coordinates: Galactic longitude/latitude system (proven effective from Cygni Arcana)

import matplotlib.pyplot as plt
import math
from collections import namedtuple
from pathlib import Path

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
from PIL import UnidentifiedImageError


plt.rcParams['font.family'] = ['Noto Sans Egyptian Hieroglyphs', 'DejaVu Sans']

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'generated'

# Color themes - Egyptian-inspired palette
THEMES = {
    'light': {
        'background': '#F5F5DC',  # Beige papyrus
        'text': '#8B4513',        # Dark brown hieroglyphic ink
        'grid': '#D2691E',        # Sandy brown grid
        'black_hole_edge': '#8B4513',
        'black_hole_glow': '#FFD700',  # Golden glow
        'sol_edge': '#FF8C00',    # Egyptian solar disc
        'star_edge': '#8B4513'
    },
    'dark': {
        'background': '#1a1a2e',  # Deep night sky
        'text': '#FFD700',        # Golden hieroglyphs
        'grid': '#B8860B',        # Dark goldenrod
        'black_hole_edge': '#FFD700',
        'black_hole_glow': '#FF8C00',
        'sol_edge': '#FF8C00',
        'star_edge': '#FFD700'
    }
}

STAR_HIEROGLYPHS = [
    # Special cases - check gardiner for magic/heka
    {"name": "Dark Energy", "distance": 26000, "longitude": 0, "latitude": 0, "size": 30,
     "hieroglyph": "𓌻", "egyptian_name": "Magic/Heka", "gardiner": "U6/A2",
     "description": "Heart of the Underworld", "color": "#000000"},

    {"name": "Dark Matter", "distance": 25900, "longitude": 0, "latitude": 0, "size": 30,
     "hieroglyph": "𓊽", "egyptian_name": "Djed Pillar", "gardiner": "R11",
     "description": "Stability Unseen", "color": "#2F4F4F"},

    {"name": "Milky Way Rotation", "distance": 26000, "longitude": 180, "latitude": 0, "size": 30,
     "hieroglyph": "𓇯", "egyptian_name": "Nut/Sky", "gardiner": "N1/C9/C23",
     "description": "Celestial Sky Goddess", "color": "#4B0082"},

    # Count=4 consensus stars
    {"name": "Sirius", "distance": 8.6, "longitude": 227, "latitude": -8.9, "size": 35,
     "hieroglyph": "𓋹", "egyptian_name": "Ankh", "gardiner": "S34",
     "description": "Life Force", "color": "#ADD8E6"},

    {"name": "Vega", "distance": 25, "longitude": 67, "latitude": 19.2, "size": 25,
     "hieroglyph": "𓂀", "egyptian_name": "Eye of Horus", "gardiner": "D10",
     "description": "Eye of Horus", "color": "#E0FFFF"},

    {"name": "Sol", "distance": 0, "longitude": 180, "latitude": 0, "size": 40,
     "hieroglyph": "𓇳", "egyptian_name": "Sun/Ra", "gardiner": "N5",
     "description": "The Solar Disc", "color": "#FFFF00"},

    {"name": "Spica", "distance": 250, "longitude": 316, "latitude": 50.8, "size": 25,
     "hieroglyph": "𓈈", "egyptian_name": "Horizon/Akhet", "gardiner": "N27",
     "description": "Horizon of Ra", "color": "#7B68EE"},

    {"name": "Polaris", "distance": 433, "longitude": 123, "latitude": 27.1, "size": 25,
     "hieroglyph": "𓃻", "egyptian_name": "Anubis", "gardiner": "E16/E17",
     "description": "Guardian of the North", "color": "#4169E1"},

    {"name": "Regulus", "distance": 79, "longitude": 226, "latitude": 48.9, "size": 25,
     "hieroglyph": "𓃠", "egyptian_name": "Bastet/Cat", "gardiner": "B1/E13",
     "description": "Lion’s Heart", "color": "#FFD700"},

    {"name": "Thuban", "distance": 303, "longitude": 97, "latitude": 47.6, "size": 25,
     "hieroglyph": "𓆓", "egyptian_name": "Cobra/Uraeus", "gardiner": "I10/I12",
     "description": "Serpent of Kingship", "color": "#228B22"},

    {"name": "Fomalhaut", "distance": 25, "longitude": 20, "latitude": -64.9, "size": 25,
     "hieroglyph": "𓆄", "egyptian_name": "Crocodile/Sobek", "gardiner": "I3/I4",
     "description": "Nile Crocodile", "color": "#00CED1"},

    {"name": "Altair", "distance": 17, "longitude": 48, "latitude": -8.9, "size": 25,
     "hieroglyph": "𓅃", "egyptian_name": "Falcon/Horus", "gardiner": "G5",
     "description": "Winged Deity", "color": "#B0E0E6"},

    {"name": "Antares", "distance": 550, "longitude": 351, "latitude": 15, "size": 30,
     "hieroglyph": "𓄤", "egyptian_name": "Heart", "gardiner": "F34",
     "description": "Scorpion’s Heart", "color": "#FF4500"},

    {"name": "Deneb", "distance": 2600, "longitude": 84, "latitude": 1.9, "size": 30,
     "hieroglyph": "𓅜", "egyptian_name": "Ibis/Thoth", "gardiner": "G26/C3",
     "description": "Scribe of the Gods", "color": "#F0FFFF"},

    {"name": "Canopus", "distance": 310, "longitude": 261, "latitude": -25.3, "size": 30,
     "hieroglyph": "𓇼", "egyptian_name": "Isis", "gardiner": "C2/C10/C20",
     "description": "Throne Goddess", "color": "#FFF5EE"},

    {"name": "Procyon", "distance": 11.5, "longitude": 213, "latitude": 13, "size": 25,
     "hieroglyph": "𓃢", "egyptian_name": "Jackal", "gardiner": "E16/E17",
     "description": "Faithful Guardian", "color": "#FFE4B5"},

    {"name": "Aldebaran", "distance": 65, "longitude": 181, "latitude": -20, "size": 25,
     "hieroglyph": "𓃬", "egyptian_name": "Lion", "gardiner": "E1/E23",
     "description": "Eye of the Bull", "color": "#FF6347"},

    {"name": "Capella", "distance": 42, "longitude": 163, "latitude": 4.6, "size": 25,
     "hieroglyph": "𓆰", "egyptian_name": "Lotus", "gardiner": "M1/M9",
     "description": "Blossom of Creation", "color": "#FFDAB9"},

    {"name": "Sheliak", "distance": 960, "longitude": 71, "latitude": -4.6, "size": 25,
     "hieroglyph": "𓇼", "egyptian_name": "Moon", "gardiner": "N11/N30",
     "description": "Cycles of Khonsu", "color": "#F5F5F5"},

    {"name": "Betelgeuse", "distance": 550, "longitude": 200, "latitude": -8.2, "size": 30,
     "hieroglyph": "𓇳", "egyptian_name": "Osiris", "gardiner": "A40/C1/C12",
     "description": "Dying and Rising God", "color": "#FF0000"},

    {"name": "Rigel", "distance": 860, "longitude": 210, "latitude": -25, "size": 30,
     "hieroglyph": "𓆣", "egyptian_name": "Scarab/Khepri", "gardiner": "L1",
     "description": "Becoming, Renewal", "color": "#87CEFA"},

    {"name": "Alpha Centauri", "distance": 4.37, "longitude": 315, "latitude": -0.7, "size": 35,
     "hieroglyph": "𓎟", "egyptian_name": "Shen Ring", "gardiner": "V9",
     "description": "Eternal Return", "color": "#FFFFFF"},

    {"name": "Acrux", "distance": 320, "longitude": 320, "latitude": -0.5, "size": 25,
     "hieroglyph": "𓅃", "egyptian_name": "Vulture", "gardiner": "G1/G14",
     "description": "Underworld Bird", "color": "#8B0000"},

    {"name": "Arcturus", "distance": 37, "longitude": 15, "latitude": 69, "size": 30,
     "hieroglyph": "𓇓", "egyptian_name": "Was Scepter", "gardiner": "S39/S40",
     "description": "Power and Dominion", "color": "#FFA500"},

    {"name": "Achernar", "distance": 139, "longitude": 300, "latitude": -58.8, "size": 30,
     "hieroglyph": "𓈗", "egyptian_name": "Water/Waves", "gardiner": "N35",
     "description": "Waters of Nun", "color": "#1E90FF"},

    # Count=3 consensus stars
    {"name": "Bellatrix", "distance": 250, "longitude": 210, "latitude": -18, "size": 25,
     "hieroglyph": "𓇼", "egyptian_name": "Star", "gardiner": "N14",
     "description": "Celestial Star", "color": "#F8F8FF"},

    {"name": "Mira", "distance": 300, "longitude": 160, "latitude": -58, "size": 25,
     "hieroglyph": "𓅛", "egyptian_name": "Ba Bird", "gardiner": "G29/G53",
     "description": "The Soul", "color": "#FFEFD5"},

    {"name": "Delta Cancri", "distance": 180, "longitude": 200, "latitude": 23, "size": 25,
     "hieroglyph": "𓆤", "egyptian_name": "Bee", "gardiner": "L2",
     "description": "Industrious Order", "color": "#FFFFE0"},

    {"name": "Alnilam", "distance": 2000, "longitude": 275, "latitude": -2, "size": 30,
     "hieroglyph": "𓌂", "egyptian_name": "Crook", "gardiner": "S38/S42",
     "description": "Shepherd’s Staff", "color": "#AFEEEE"},

    {"name": "Albireo", "distance": 430, "longitude": 62, "latitude": 5, "size": 25,
     "hieroglyph": "𓆣", "egyptian_name": "Double Crown", "gardiner": "S4/S5",
     "description": "Union of Two Lands", "color": "#DA70D6"},

    {"name": "Algol", "distance": 93, "longitude": 150, "latitude": -22, "size": 25,
     "hieroglyph": "𓆄", "egyptian_name": "Feather/Maat", "gardiner": "H6",
     "description": "Star of Fate", "color": "#DC143C"},

    {"name": "Mizar", "distance": 86, "longitude": 160, "latitude": 55, "size": 25,
     "hieroglyph": "𓌢", "egyptian_name": "Flail", "gardiner": "S45",
     "description": "Royal Authority", "color": "#F5DEB3"},

    {"name": "Pleiades", "distance": 444, "longitude": 167, "latitude": -23, "size": 30,
     "hieroglyph": "𓃞", "egyptian_name": "Hathor/Cow", "gardiner": "E1/E4/C9",
     "description": "Seven Sisters", "color": "#87CEEB"},

    {"name": "Hadar", "distance": 390, "longitude": 315, "latitude": 1.3, "size": 30,
     "hieroglyph": "𓃩", "egyptian_name": "Hippopotamus", "gardiner": "E24/E25",
     "description": "River Beast", "color": "#A9A9A9"},

    {"name": "Van Maanen's Star", "distance": 14, "longitude": 70, "latitude": -34, "size": 20,
     "hieroglyph": "𓂓", "egyptian_name": "Ka", "gardiner": "D28",
     "description": "Vital Essence", "color": "#FFFFFF"},

    {"name": "Saiph", "distance": 720, "longitude": 200, "latitude": -18, "size": 25,
     "hieroglyph": "𓏠", "egyptian_name": "Offering Table", "gardiner": "R3/R4/R7",
     "description": "Sacred Offering", "color": "#D8BFD8"},
]

# Coordinate system preserved from Cygni Arcana (proven effective)
CartesianCoords = namedtuple('CartesianCoords', ['x_plot', 'y_plot'])

def galactic_to_cartesian(distance, longitude_deg, latitude_deg):
    """Convert galactic coordinates to cartesian for plotting (preserved from Cygni Arcana)"""
    longitude_rad = math.radians(longitude_deg)
    latitude_rad = math.radians(latitude_deg)
    planar_distance = distance * math.cos(latitude_rad)
    x_plot = planar_distance * math.sin(longitude_rad)
    y_plot = planar_distance * math.cos(longitude_rad)
    return CartesianCoords(x_plot, y_plot)

def categorize_x_plot(perpendicular_distance):
    """Categorize perpendicular distance for plotting (preserved from Cygni Arcana)"""
    abs_distance = abs(perpendicular_distance)
    sign = -1 if perpendicular_distance >= 0 else 1

    if abs_distance < 1:
        return 0
    elif abs_distance < 12:
        return sign * 0.5
    elif abs_distance < 50:
        return sign * 1
    elif abs_distance < 160:
        return sign * 1.7
    else:
        return sign * 2.3

def rank_y_plot(star_data, all_stars):
    """Calculate y-position based on ordinal ranking (adapted from Cygni Arcana)"""
    star_name = star_data['name']

    # Special reference points
    if star_name == "Sagittarius A*":
        return 0.7
    elif star_name == "Sol":
        return 0

    # Regular star ranking logic (preserved)
    regular_stars = []
    for star in all_stars:
        if star['name'] not in ["Sagittarius A*", "Sol"]:
            coords = galactic_to_cartesian(star['distance'], star['longitude'], star['latitude'])
            regular_stars.append({'name': star['name'], 'y_plot': coords.y_plot})

    regular_stars.sort(key=lambda x: x['y_plot'], reverse=True)
    star_coords = galactic_to_cartesian(star_data['distance'], star_data['longitude'], star_data['latitude'])
    current_y_plot = star_coords.y_plot

    if current_y_plot > 0:
        positive_stars = [s for s in regular_stars if s['y_plot'] > 0]
        if star_name in [s['name'] for s in positive_stars]:
            rank = [s['name'] for s in positive_stars].index(star_name)
            total_positive = len(positive_stars)
            reversed_rank = total_positive - 1 - rank
            return 0.1 + (reversed_rank / (total_positive - 1)) * 0.47 if total_positive > 1 else 0.35
    else:
        negative_stars = [s for s in regular_stars if s['y_plot'] <= 0]
        if star_name in [s['name'] for s in negative_stars]:
            rank = [s['name'] for s in negative_stars].index(star_name)
            total_negative = len(negative_stars)
            return -0.1 - (rank / (total_negative - 1)) * 0.47 if total_negative > 1 else -0.35

    return 0


# markone
def plot_star_hieroglyph(ax, star, all_stars, theme):
    """Enhanced star-hieroglyph plotting with better image handling and layout"""
    coords = galactic_to_cartesian(star['distance'], star['longitude'], star['latitude'])
    x_pos = categorize_x_plot(coords.x_plot)
    y_pos = rank_y_plot(star, all_stars)

    # Dynamic sizing based on star importance and type
    size_mapping = {
        "Sol": 50,
        "Sirius": 45,
        "Alpha Centauri": 45,
        "Dark Energy": 40,
        "Dark Matter": 40,
        "Milky Way Rotation": 40,
        "Sagittarius A*": 35
    }
    size = size_mapping.get(star['name'], 35)

    # Enhanced special handling for different star types
    if star['name'] == "Sagittarius A*" or "Dark" in star['name']:
        # Black hole / dark matter visualization
        ax.scatter(x_pos, y_pos, s=size * 12, c=theme['black_hole_glow'],
                   marker='o', alpha=0.4, zorder=2)
        ax.scatter(x_pos, y_pos, s=size * 10, facecolors='none',
                   edgecolors=theme['black_hole_edge'], linewidth=2, zorder=3)
        ax.scatter(x_pos, y_pos, s=size * 6, c=theme['background'],
                   marker='o', edgecolors=theme['black_hole_edge'], linewidth=1, zorder=4)
        edgecolor = theme['black_hole_edge']
    elif star['name'] == "Sol":
        # Solar disc with enhanced glow
        ax.scatter(x_pos, y_pos, s=size * 12, c='#FFD700', alpha=0.3, zorder=2)
        ax.scatter(x_pos, y_pos, s=size * 10, c=star['color'],
                   marker='o', edgecolors=theme['sol_edge'], linewidth=2, zorder=3, alpha=0.9)
        edgecolor = theme['sol_edge']
    else:
        # Regular stars with subtle glow
        ax.scatter(x_pos, y_pos, s=size * 11, c=star['color'], alpha=0.2, zorder=2)
        ax.scatter(x_pos, y_pos, s=size * 10, c=star['color'],
                   marker='o', edgecolors=theme['star_edge'], linewidth=1, zorder=3, alpha=0.8)
        edgecolor = theme['star_edge']

    # Improved hieroglyph positioning and handling
    glyph_x = x_pos + 0.12
    glyph_loaded = False
    file_type_used = "None"

    # Now only try to load PNG files
    glyph_name = star['egyptian_name'].lower().replace(' ', '_').replace('/', '_')
    glyph_path = PROJECT_ROOT / 'glyph' / f"{glyph_name}.png"

    try:
        if glyph_path.exists():
            img = plt.imread(str(glyph_path))
            file_type_used = "PNG"

            # Enhanced transparency handling
            if len(img.shape) == 3 and img.shape[-1] == 3:  # RGB image, add alpha
                import numpy as np
                white_threshold = 0.95
                is_background = np.all(img >= white_threshold, axis=2)
                alpha = np.where(is_background, 0, 1)
                img = np.dstack((img, alpha))
                print(f"  Added transparency to PNG")

            # Much larger, adaptive zoom
            base_zoom = 0.04 if star['name'] in ["Sol", "Sirius", "Alpha Centauri"] else 0.035

            imagebox = OffsetImage(img, zoom=base_zoom)
            ab = AnnotationBbox(imagebox, (glyph_x, y_pos), xybox=(0, 0),
                                xycoords='data', boxcoords="offset points",
                                pad=0, frameon=False, zorder=5)
            ax.add_artist(ab)

            glyph_loaded = True
            label_x = glyph_x + 0.12  # More spacing for larger glyphs
            print(f"✓ PNG rendered for {star['name']} {star['hieroglyph']}   {glyph_name} at zoom {base_zoom}")

    except Exception as e:
        print(f"✗ Failed to load {glyph_path}: {e}")

    # Fallback to Unicode hieroglyph if no image loaded
    if not glyph_loaded:
        print(f"→ Using Unicode fallback for {star['name']}: {star['hieroglyph']} {glyph_name}")
        # Enhanced Unicode rendering with better positioning
        font_size = 14 if star['name'] in ["Sol", "Sirius", "Alpha Centauri"] else 12
        ax.text(glyph_x, y_pos, star['hieroglyph'], ha='center', va='center',
                fontsize=font_size, color=theme['text'], zorder=5,
                fontfamily=['Noto Sans Egyptian Hieroglyphs', 'DejaVu Sans'])
        label_x = glyph_x + 0.06

    # Enhanced label formatting with better typography
    distance_str = f"{star['distance']}" if star['distance'] != int(star['distance']) else f"{int(star['distance'])}"
    combined_label = f"{star['name']} ({distance_str} ly) • {star['egyptian_name']}"

    # Adaptive font sizing based on label length and star importance
    base_font_size = 9 if star['name'] in ["Sol", "Sirius", "Alpha Centauri"] else 8
    font_size = max(6, base_font_size - len(combined_label) // 20)  # Scale down for long labels

    ax.text(label_x, y_pos, combined_label, ha='left', va='center',
            fontsize=font_size, color=theme['text'], zorder=5,
            fontweight='bold' if star['name'] in ["Sol", "Sirius"] else 'normal')

    return glyph_loaded, file_type_used  # Return success status and file type used
# markone




def setup_hieroglyphic_plot(ax, theme):
    """Configure plot appearance with Egyptian astronomical theme"""
    ax.set_xlim(-2.6, 3.2)  # Slightly wider for hieroglyphic labels
    ax.set_ylim(-0.65, 0.65)

    # Grid lines
    x_ticks = [-2.3, -1.7, -1, -0.5, 0, 0.5, 1, 1.7, 2.3]
    ax.set_xticks([])
    ax.set_yticks([])

    for x_val in x_ticks:
        if x_val == 0:
            ax.axvline(x=x_val, color='#FFD700', alpha=0.8, linestyle='--', linewidth=0.75)
        else:
            ax.axvline(x=x_val, color=theme['grid'], alpha=0.45, linestyle='--', linewidth=0.45)

    # Curved arrow for cosmic navigation
    from matplotlib.patches import FancyArrowPatch
    arrow = FancyArrowPatch((-1.5, -0.60), (1.5, -0.60),
                            connectionstyle="arc3,rad=0.05",
                            arrowstyle='<-', mutation_scale=20,
                            color='#FFD700', alpha=0.6, linewidth=1, linestyle='--')
    ax.add_patch(arrow)

def create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size='A3'):
    """Create Egyptian hieroglyphic star map with configurable paper sizes"""

    # Paper size configurations (ISO 216)
    paper_dimensions = {
        'A4': (11.7, 8.3),   # 26 stars baseline
        'A3': (16.5, 11.7),  # 55-100 stars (testing range)
        'A2': (23.4, 16.5),  # ~150 stars
        'A1': (33.1, 23.4),  # ~200 stars
        'A0': (46.8, 33.1)   # ~450 stars
    }

    current_theme = THEMES['dark' if dark_mode else 'light']
    figsize = paper_dimensions.get(paper_size, paper_dimensions['A3'])

    fig, ax = plt.subplots(figsize=figsize, facecolor=current_theme['background'])
    ax.set_facecolor(current_theme['background'])

    # Plot all star-hieroglyph pairs
    for star in STAR_HIEROGLYPHS:
        plot_star_hieroglyph(ax, star, STAR_HIEROGLYPHS, current_theme)

    setup_hieroglyphic_plot(ax, current_theme)

    # Remove plot borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Force matplotlib to use the hieroglyphic font
    plt.tight_layout()

    # Save with descriptive filename
    mode_suffix = '_dark' if dark_mode else '_light'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f'hieroglyphic_cosmos_{paper_size.lower()}_landscape{mode_suffix}.pdf'

    plt.savefig(output_file, dpi=300, bbox_inches='tight',
                facecolor=current_theme['background'])
    plt.close()

    print(f"Generated: {output_file}")
    print(f"Star-Hieroglyph pairs: {len(STAR_HIEROGLYPHS)}")
    print(f"Paper size: {paper_size} ({figsize[0]:.1f}\" x {figsize[1]:.1f}\")")

# Generate test plots for density evaluation
if __name__ == "__main__":
    # Create A3 versions for density testing (current 15 pairs)
    create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size='A3')
    # create_hieroglyphic_cosmos_plot(dark_mode=False, paper_size='A3')
