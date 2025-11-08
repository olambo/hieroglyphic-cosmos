# AI Development Partners:
#     - Claude (Anthropic): Code adaptation from Cygni Arcana, coordinate system preservation,
#       Egyptian astronomical research integration, and hieroglyphic mapping framework
#     - Previous Cygni Arcana contributors: Grok (xAI), ChatGPT (OpenAI), Gemini (Google)
#
# This project represents the evolution from tarot-stellar mapping to historically-graunded
# Egyptian hieroglyphic-stellar connections, maintaining astronomical precision while
# embracing authentic ancient Egyptian cosmic symbolism.
#
# DATA SOURCES & COORDINATE SYSTEM:
# - STELLAR COORDINATES HAVE BEEN VERIFIED BY SIMBAD QUERIES
# - Egyptian stellar references: Neugebauer & Parker, Lull & Belmonte, ancient star maps
# - Hieroglyphic sources: Gardiner sign list, Budge hieroglyphic dictionary

import matplotlib.pyplot as plt
import math
import sys
from collections import namedtuple
from pathlib import Path

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
from PIL import UnidentifiedImageError

sys.path.append(str(Path(__file__).parent))
# Assuming star_glyphs.py exists and contains STAR_HIEROGLYPHS
try:
    from star_glyphs import STAR_HIEROGLYPHS
except ImportError:
    print("WARNING: Could not import STAR_HIEROGLYPHS. Using a dummy list for compilation.")
    STAR_HIEROGLYPHS = []


plt.rcParams["font.family"] = ["Noto Sans Egyptian Hieroglyphs", "DejaVu Sans"]

# -------------------------------
# ⭐️ MANUAL PLOT ADJUSTMENTS ⭐️
# Use this dictionary to manually offset the Y-axis (latitude) of crowded stars.
# Add an entry here, re-run the script, and check the new plot.
MANUAL_NUDGES = {
    # Galactic Center (GC) Adjustments
    "Dark Energy": 0.58,
    "Dark Matter": 0.58,
    # # Quadrant 1 Adjustments
    "Ras Algethi": -0.02,
    "Sabik": 0.02,
    "Fomalhaut": -0.02,
    "Altair": -0.025,
    "Alphecca": -0.03,
    "Unukalhai": 0.005,
    # Quadrant 2 Adjustments
    "Delta Cephei": 0.017,
    "Kochab": -0.009,
    "Dubhe": 0.03,
    "Capella": 0.02,
    "Elnath": -0.15,
    "Mira": -0.12,
    "Almach": -0.025,
    # Quadrant 3 Adjustments
    "Sirius": 0.05,
    "Procyon": 0.02,
    "Aldebaran": -0.05,
    "Alnilam": 0.055,
    "Betelgeuse": 0.03,
    # Quadrant 4 Adjustments
    "Kaus Australis": 0.1,
    "Delta Pavonis": -0.05,
    "Miaplacidus": -0.015,
    "Epsilon Indi": -0.06,
    "Alpha Centauri": -0.06,
    # Galactic Anti-Center (GAC) Adjustments
    "Milky Way Rotation": -0.59,
}
# -------------------------------


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "generated"

# Color themes - Egyptian-inspired palette
THEMES = {
    "light": {
        "background": "#F5F5DC",  # Beige papyrus
        "text": "#8B4513",  # Dark brown hieroglyphic ink
        "grid": "#D2691E",  # Sandy brown grid
        "black_hole_edge": "#8B4513",
        "black_hole_glow": "#FFD700",  # Golden glow
        "sol_edge": "#FF8C00",  # Egyptian solar disc
        "star_edge": "#8B4513",
    },
    "dark": {
        "background": "#1a1a2e",  # Deep night sky
        "text": "#FFD700",  # Golden hieroglyphs
        "grid": "#B8860B",  # Dark goldenrod
        "black_hole_edge": "#FFD700",
        "black_hole_glow": "#FF8C00",
        "sol_edge": "#FF8C00",
        "star_edge": "#FFD700",
    },
}


# Coordinate system preserved from Cygni Arcana (proven effective)
CartesianCoords = namedtuple("CartesianCoords", ["x_plot", "y_plot"])


def galactic_to_cartesian(distance, longitude_deg, latitude_deg):
    """Convert galactic coordinates to cartesian for plotting (preserved from Cygni Arcana)"""
    longitude_rad = math.radians(longitude_deg)
    latitude_rad = math.radians(latitude_deg)
    planar_distance = distance * math.cos(latitude_rad)
    x_plot = planar_distance * math.sin(longitude_rad)
    y_plot = planar_distance * math.cos(longitude_rad)
    return CartesianCoords(x_plot, y_plot)


# Grid lines - Restricted to 0.6, 1.2, 1.9, 2.5
x_ticks = [-2.5, -1.9, -1.2, -0.6, 0, 0.6, 1.2, 1.9, 2.5]


# --- NEW CONSTANTS FOR Y-AXIS SCALING (User-specified) ---
# Assigned Light-Year distances for each X-Plot bucket, used only for Y-axis normalization.
BUCKET_LY_DISTANCES = {
    0.6: 10,  # Very Near
    1.2: 50,  # Near
    1.9: 150,  # Far
    2.5: 250,  # Very Far (All remaining distant stars)
}
MAX_Y_PLOT_SPREAD = 0.55  # Represents the maximum vertical spread (half the total y-plot range)


def categorize_x_plot(perpendicular_distance):
    """
    Categorize perpendicular distance for plotting.
    All stars falling outside the 'far' threshold are now mapped to the 2.5 bucket.
    """
    abs_distance = abs(perpendicular_distance)
    sign = -1 if perpendicular_distance >= 0 else 1

    if abs_distance < 0.4:  # GC-Sol
        return 0
    elif sign == -1 and abs_distance < 13:  # very near
        return sign * 0.6
    elif sign == 1 and abs_distance < 8:  # very near
        return sign * 0.6
    elif sign == -1 and abs_distance < 45:  # near
        return sign * 1.2
    elif sign == 1 and abs_distance < 50:  # near
        return sign * 1.2
    elif sign == -1 and abs_distance < 175:  # far
        return sign * 1.9
    elif sign == 1 and abs_distance < 160:  # far
        return sign * 1.9
    else:  # All other stars (including Deneb, Delta Cephei) are mapped to the final 2.5 bucket
        return sign * 2.5


# ----------------------------------------------------
# ⭐️ FINAL: Function to calculate Y-position using fixed Bucket LY Distance ⭐️
# ----------------------------------------------------


def calc_y_plot(star_data, x_plot_position):
    """
    Calculates y-position using Longitude (l) for the sign and scales the result
    such that distant buckets have a greater vertical spread, compensating for
    the overall negative bias in the star set's Longitude distribution.
    """
    star_name = star_data["name"]
    longitude_deg = star_data["longitude"]

    # 1. SPECIAL CASE HANDLING (remains the same)
    if star_name in ["Sagittarius A*", "Sol", "Dark Energy", "Dark Matter", "Milky Way Rotation"]:
        if star_name == "Sagittarius A*":
            return 0.7
        return 0

    # 2. Get the assigned BUCKET DISTANCE (in Light Years)
    bucket_key = round(abs(x_plot_position), 1)
    assigned_ly_distance = BUCKET_LY_DISTANCES.get(bucket_key, 300.0)

    # 3. Calculate Base Y-Position using Longitude (l)
    longitude_rad = math.radians(longitude_deg)
    base_y_coord = math.cos(longitude_rad)  # Range: [-1.0, 1.0]

    # 4. Apply Scaling Factor for Correct Spread and Utilization

    MAX_BUCKET_LY_DISTANCE = 300.0

    # Spread Factor: Scales the assigned distance against the max distance (0.05 to 1.0)
    spread_factor = assigned_ly_distance / MAX_BUCKET_LY_DISTANCE

    # ⭐️ FIX: Increase the MAX_Y_SPREAD_MULTIPLIER to push the max Y-value closer to the limit. ⭐️
    # This compensates for the negative bias in the cos(l) distribution of your star set.
    # Increasing by 10% (0.55 * 1.1 = 0.605) should push the upper limit out.
    MAX_Y_PLOT_LIMIT = 0.55
    MAX_Y_SPREAD_MULTIPLIER = MAX_Y_PLOT_LIMIT * 1.1
    MIN_Y_SPREAD_MULTIPLIER = 0.20

    # Range that spread_factor modulates: MAX_Y_SPREAD_MULTIPLIER - MIN_Y_SPREAD_MULTIPLIER
    range_modulation = MAX_Y_SPREAD_MULTIPLIER - MIN_Y_SPREAD_MULTIPLIER

    # Final Spread Multiplier: Linearly interpolates the spread.
    final_spread_multiplier = (range_modulation * spread_factor) + MIN_Y_SPREAD_MULTIPLIER

    # Final Y Position
    final_y_position = base_y_coord * final_spread_multiplier

    # Ensure the final result is strictly within the original fixed plot limits (0.55)
    return min(MAX_Y_PLOT_LIMIT, max(-MAX_Y_PLOT_LIMIT, final_y_position))


# mark-s
# Gardiner code to actual PNG filename mapping (for variants)
GARDINER_PNG_MAP = {
    "O24": "US22O24A.png",
    "S34": "US22S34A.png",
    "S42": "US22S42A.png",
    # Add others as you discover them
}


def find_stellar_png(gardiner_code):
    """Try each Gardiner code variant with explicit mapping"""
    for code in gardiner_code.split("/"):
        code = code.strip()

        # Check explicit mapping first
        if code in GARDINER_PNG_MAP:
            glyph_path = PROJECT_ROOT / "data" / "stellar_pngs" / GARDINER_PNG_MAP[code]
            if glyph_path.exists():
                return glyph_path

        # Try standard naming
        glyph_path = PROJECT_ROOT / "data" / "stellar_pngs" / f"US22{code}.png"
        if glyph_path.exists():
            return glyph_path

    return None


# Manual overrides for specific problem glyphs
GLYPH_ZOOM_OVERRIDES = {
    "S34A": 0.03,  # Ankh/Sirius - intrinsically large
    "S4": 0.025,  # Albireo - also too big at default
    # Add others as you find them
}


# mark
def prepare_plot_data(star_list, nudge_dict):
    """
    Calculates both X (distance bucket) and Y (physical spread + nudge)
    coordinates for all stars, centralizing all logic here.
    """
    plot_data = []

    for star in star_list:
        new_star = star.copy()
        star_name = new_star.get("name")

        # 1. Calculate Cartesian Coordinates
        coords = galactic_to_cartesian(star["distance"], star["longitude"], star["latitude"])

        # 2. Calculate X-axis position (Categorize based on X_plot)
        final_x = categorize_x_plot(coords.x_plot)
        new_star["x_plot_position"] = final_x

        # 3. Calculate Y-position (using the new bucket-scaled function)
        base_y_position = calc_y_plot(star, final_x)

        # 4. Apply Nudge and store final Y-position
        nudge_amount = nudge_dict.get(star_name, 0.0)
        final_y = base_y_position + nudge_amount
        new_star["y_plot_position"] = final_y

        plot_data.append(new_star)

    return plot_data


# mark
def plot_star_hieroglyph(ax, star, all_stars, theme):
    """Enhanced star-hieroglyph plotting with two-line label layout"""

    # ⭐️ Use the pre-calculated positions directly ⭐️
    x_pos = star["x_plot_position"]
    y_pos = star["y_plot_position"]

    size_mapping = {
        "Sol": 50,
        # "Sirius": 45,
        # "Alpha Centauri": 45,
        "Dark Energy": 40,
        "Dark Matter": 40,
        "Milky Way Rotation": 40,
        # "Sagittarius A*": 35,
    }
    size = size_mapping.get(star["name"], 35)

    # Star background rendering
    if star["name"] == "Dark Energy":
        pass
    elif star["name"] == "Sagittarius A*" or "Dark" in star["name"] or star["egyptian_name"] == "Nut/Sky":
        # 1. Define Nut's specific color
        inner_edge_color = (
            "#87CEEB"  #  light sky blue
            if star["egyptian_name"] == "Nut/Sky"
            else theme["black_hole_edge"]
        )

        ax.scatter(
            x_pos,
            y_pos,
            s=size * 12,
            c=theme["black_hole_glow"],
            marker="o",
            alpha=0.4,
            zorder=2,
        )
        ax.scatter(
            x_pos,
            y_pos,
            s=size * 10,
            facecolors="none",
            edgecolors=theme["black_hole_edge"],
            linewidth=2,
            zorder=3,
        )
        ax.scatter(
            x_pos,
            y_pos,
            s=size * 6,
            c=theme["background"],
            marker="o",
            edgecolors=inner_edge_color,
            linewidth=1,
            zorder=4,
        )
    elif star["name"] == "Sol":
        ax.scatter(x_pos, y_pos, s=size * 12, c="#FFD700", alpha=0.3, zorder=2)
        ax.scatter(
            x_pos,
            y_pos,
            s=size * 10,
            c=star["color"],
            marker="o",
            edgecolors=theme["sol_edge"],
            linewidth=2,
            zorder=3,
            alpha=0.9,
        )
    else:
        ax.scatter(x_pos, y_pos, s=size * 11, c=star["color"], alpha=0.2, zorder=2)
        ax.scatter(
            x_pos,
            y_pos,
            s=size * 10,
            c=star["color"],
            marker="o",
            edgecolors=theme["star_edge"],
            linewidth=1,
            zorder=3,
            alpha=0.8,
        )

    # NEW: Dark Energy goes to the LEFT
    if star["name"] == "Dark Energy":
        glyph_x = x_pos - 0.13  # Flip to left side
    else:
        glyph_x = x_pos + 0.12

    # Render PNG only (no Unicode)
    glyph_rendered = False
    if glyph_path := find_stellar_png(star["gardiner"]):
        try:
            img = plt.imread(str(glyph_path))
            height, width = img.shape[0], img.shape[1]
            # Aspect ratio logic (remains the same)
            aspect_ratio = height / width

            if len(img.shape) == 3 and img.shape[-1] == 3:
                import numpy as np

                white_threshold = 0.95
                is_background = np.all(img >= white_threshold, axis=2)
                alpha = np.where(is_background, 0, 1)
                img = np.dstack((img, alpha))

            glyph_filename = glyph_path.name.replace("US22", "").replace(".png", "")
            if glyph_filename in GLYPH_ZOOM_OVERRIDES:
                base_zoom = GLYPH_ZOOM_OVERRIDES[glyph_filename]
            else:
                base_zoom = 0.035
                if aspect_ratio > 2.5:
                    base_zoom *= 0.4
                elif aspect_ratio > 2.0:
                    base_zoom *= 0.5
                elif aspect_ratio > 1.5:
                    base_zoom *= 0.65
                elif aspect_ratio > 1.3:
                    base_zoom *= 0.8

            imagebox = OffsetImage(img, zoom=base_zoom)
            ab = AnnotationBbox(
                imagebox,
                (glyph_x, y_pos),
                xybox=(0, 0),
                xycoords="data",
                boxcoords="offset points",
                pad=0,
                frameon=False,
                zorder=5,
            )
            ax.add_artist(ab)
            glyph_rendered = True
        except Exception as e:
            print(f"✗ PNG failed for {star['name']}: {e}")

    # Two-line label layout
    # NEW: Dark Energy labels go to the LEFT
    if star["name"] == "Dark Energy":
        label_x = glyph_x - 0.35  # Flip label to left side
        label_ha = "left"
    else:
        label_x = glyph_x + 0.06
        label_ha = "left"

    # Line 1: Egyptian name in white
    egyptian_y = y_pos + 0.007
    ax.text(
        label_x,
        egyptian_y,
        star["egyptian_name"],
        ha=label_ha,
        va="center",
        fontsize=9,
        color="white",
        zorder=5,
    )

    # Line 2: Star name + Longitude + distance in theme color

    if star["name"] in ["Dark Matter", "Dark Energy", "Milky Way Rotation"]:
        star_label = star["name"]
    else:
        # ⭐️ MODIFICATION: Add Galactic Longitude (l) ⭐️
        longitude_deg = star["longitude"]
        # Format longitude to one decimal place
        longitude_str = f"l={longitude_deg:.1f}°"

        distance_str = (
            f"{star['distance']}" if star["distance"] != int(star["distance"]) else f"{int(star['distance'])}"
        )
        # star_label = f"{star['name']} ({longitude_str}, {distance_str} ly)" # Updated label format
        # star_label = f"{star['name']} ({distance_str} ly)"
        star_label = star["name"]

    # colors for Dark Matter/Energy labels
    if star["name"] == "Dark Energy":
        label_color = "#FF6B6B"  # Lighter warm red
    elif star["name"] == "Dark Matter":
        label_color = "#66D9EF"  # Bright cyan
    else:
        label_color = theme["text"]

    star_y = y_pos - 0.01

    ax.text(
        label_x,
        star_y,
        star_label,
        ha=label_ha,
        va="center",
        fontsize=8,
        color=label_color,
        zorder=5,
    )

    return glyph_rendered


# mark


def setup_hieroglyphic_plot(ax, theme):
    """Configure plot appearance with Egyptian astronomical theme"""
    # X-limit adjusted to the max bucket of 2.5
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-0.65, 0.65)

    # xticks Grid lines
    ax.set_xticks([])
    ax.set_yticks([])

    for x_val in x_ticks:
        if x_val == 0:
            ax.axvline(x=x_val, color="#FFD700", alpha=0.8, linestyle="--", linewidth=0.75)
        else:
            ax.axvline(x=x_val, color=theme["grid"], alpha=0.45, linestyle="--", linewidth=0.45)

    # Curved arrow for cosmic navigation
    from matplotlib.patches import FancyArrowPatch

    arrow = FancyArrowPatch(
        (-1.5, -0.60),
        (1.5, -0.60),
        connectionstyle="arc3,rad=0.05",
        arrowstyle="<-",
        mutation_scale=20,
        color="#FFD700",
        alpha=0.6,
        linewidth=1,
        linestyle="--",
    )
    ax.add_patch(arrow)


def create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size="A3"):
    """Create Egyptian hieroglyphic star map with configurable paper sizes"""

    # Paper size configurations (ISO 216)
    paper_dimensions = {
        "A4": (11.7, 8.3),  # 26 stars baseline
        "A3": (16.5, 11.7),  # 55-100 stars (testing range)
        "A2": (23.4, 16.5),  # ~150 stars
        "A1": (33.1, 23.4),  # ~200 stars
        "A0": (46.8, 33.1),  # ~450 stars
    }

    current_theme = THEMES["dark" if dark_mode else "light"]
    figsize = paper_dimensions.get(paper_size, paper_dimensions["A3"])

    fig, ax = plt.subplots(figsize=figsize, facecolor=current_theme["background"])
    ax.set_facecolor(current_theme["background"])

    # Watermark - diagonal across center
    ax.text(
        0,  # Centered
        0,  # Centered vertically
        "         PREVIEW COPY • NOT FOR DISTRIBUTION",
        ha="center",
        va="center",
        fontsize=18,
        color="#FFFFFF",
        alpha=0.25,
        rotation=45,
        weight="bold",
        zorder=10,
        family="monospace",
    )

    # ⭐️ UPDATED: Prepare the data with all calculated positions ⭐️
    plot_ready_stars = prepare_plot_data(STAR_HIEROGLYPHS, MANUAL_NUDGES)

    # Plot all star-hieroglyph pairs
    for star in plot_ready_stars:
        # NOTE: all_stars parameter is technically unused in the current plot_star_hieroglyph
        # but kept for API compatibility with legacy code/future extensions.
        plot_star_hieroglyph(ax, star, STAR_HIEROGLYPHS, current_theme)

    # NEW: Add Galactic Center label above Dark Matter/Dark Energy cluster
    gc_y_position = 0.62  # Adjust this to position above the cluster
    ax.text(
        0,  # Centered at x=0
        gc_y_position,
        "Galactic Center",
        ha="center",
        va="center",
        fontsize=10,
        color="#FFD700",  # Golden color
        weight="bold",
        zorder=5,
    )

    setup_hieroglyphic_plot(ax, current_theme)

    # Remove plot borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Force matplotlib to use the hieroglyphic font
    plt.tight_layout()

    # Save with descriptive filename
    mode_suffix = "_dark" if dark_mode else "_light"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"hieroglyphic_cosmos_{paper_size.lower()}_landscape{mode_suffix}.pdf"

    plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor=current_theme["background"])
    plt.close()

    print(f"Generated: {output_file}")
    print(f"Star-Hieroglyph pairs: {len(STAR_HIEROGLYPHS)}")
    print(f'Paper size: {paper_size} ({figsize[0]:.1f}" x {figsize[1]:.1f}")')


# Generate
if __name__ == "__main__":
    create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size="A3")
