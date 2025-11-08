# AI Development Partners:
#     - Claude (Anthropic): Code adaptation from Cygni Arcana, coordinate system preservation,
#       Egyptian astronomical research integration, and hieroglyphic mapping framework
#     - Previous Cygni Arcana contributors: Grok (xAI), ChatGPT (OpenAI), Gemini (Google)
#
# This project represents the evolution from tarot-stellar mapping to historically-grounded
# Egyptian hieroglyphic-stellar connections, maintaining astronomical precision while
# embracing authentic ancient Egyptian cosmic symbolism.
#
# DATA SOURCES & COORDINATE SYSTEM:
# - STELLAR COORDINATES HAVE BEEN VERIFIED BY SIMBAD QUERIES
# - Egyptian stellar references: Neugebauer & Parker, Lull & Belmonte, ancient star maps
# - Hieroglyphic sources: Gardiner sign list, Budge hieroglyphic dictionary

import math
from collections import namedtuple
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import FancyArrowPatch
from star_glyphs import STAR_HIEROGLYPHS


plt.rcParams["font.family"] = ["Noto Sans Egyptian Hieroglyphs", "DejaVu Sans"]


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "generated"

# Paper size configurations (ISO 216)
PAPER_DIMENSIONS = {
    "A4": (11.7, 8.3),  # 26 stars baseline
    "A3": (16.5, 11.7),  # 55-100 stars (testing range)
    "A2": (23.4, 16.5),  # ~150 stars
    "A1": (33.1, 23.4),  # ~200 stars
    "A0": (46.8, 33.1),  # ~450 stars
}


# ============================================================================
# COORDINATE SYSTEM CONSTANTS (from Cygni Arcana)
# ============================================================================

# Grid lines - Restricted to 0.6, 1.2, 1.9, 2.5
X_TICKS = [-2.5, -1.9, -1.2, -0.6, 0, 0.6, 1.2, 1.9, 2.5]

# Assigned Light-Year distances for each X-Plot bucket, used for Y-axis normalization
BUCKET_LY_DISTANCES = {
    0.6: 10,  # Very Near
    1.2: 50,  # Near
    1.9: 150,  # Far
    2.5: 250,  # Very Far (All remaining distant stars)
}

MAX_Y_PLOT_SPREAD = 0.55  # Maximum vertical spread (half the total y-plot range)


# ============================================================================
# RENDERING CONSTANTS
# ============================================================================

# Gardiner code to actual PNG filename mapping (for variants)
GARDINER_PNG_MAP = {
    "O24": "US22O24A.png",
    "S34": "US22S34A.png",
    "S42": "US22S42A.png",
    # Add others as you discover them
}

# Manual overrides for specific problem glyphs
GLYPH_ZOOM_OVERRIDES = {
    "S34A": 0.03,  # Ankh/Sirius - intrinsically large
    "S4": 0.025,  # Albireo - also too big at default
    # Add others as you find them
}

# Star size overrides
STAR_SIZE_OVERRIDES = {
    "Sol": 50,
    "Dark Energy": 40,
    "Dark Matter": 40,
    "Milky Way Rotation": 40,
}

# Layout constants for glyph and label positioning
GLYPH_X_OFFSET = 0.12
DARK_ENERGY_GLYPH_X_OFFSET = -0.13
LABEL_X_OFFSET = 0.06
DARK_ENERGY_LABEL_X_OFFSET = -0.35
EGYPTIAN_NAME_Y_OFFSET = 0.007
STAR_NAME_Y_OFFSET = -0.01


# ============================================================================
# COLOR THEMES - Egyptian-inspired palette
# ============================================================================

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


# ============================================================================
# MANUAL PLOT ADJUSTMENTS
# ============================================================================
# Use this dictionary to manually offset the Y-axis (latitude) of crowded stars.
# Add an entry here, re-run the script, and check the new plot.

MANUAL_NUDGES = {
    # Galactic Center (GC) Adjustments
    "Dark Energy": 0.58,
    "Dark Matter": 0.58,
    # Quadrant 1 Adjustments
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


# ============================================================================
# COORDINATE SYSTEM (Preserved from Cygni Arcana - proven effective)
# ============================================================================

CartesianCoords = namedtuple("CartesianCoords", ["x_plot", "y_plot"])


def galactic_to_cartesian(distance, longitude_deg, latitude_deg):
    """Convert galactic coordinates to cartesian for plotting (preserved from Cygni Arcana)"""
    longitude_rad = math.radians(longitude_deg)
    latitude_rad = math.radians(latitude_deg)
    planar_distance = distance * math.cos(latitude_rad)
    x_plot = planar_distance * math.sin(longitude_rad)
    y_plot = planar_distance * math.cos(longitude_rad)
    return CartesianCoords(x_plot, y_plot)


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


def calc_y_plot(star_data, x_plot_position):
    """
    Calculates y-position using Longitude (l) for the sign and scales the result
    such that distant buckets have a greater vertical spread, compensating for
    the overall negative bias in the star set's Longitude distribution.
    """
    star_name = star_data["name"]
    longitude_deg = star_data["longitude"]

    # Special case handling
    if star_name in ["Sagittarius A*", "Sol", "Dark Energy", "Dark Matter", "Milky Way Rotation"]:
        if star_name == "Sagittarius A*":
            return 0.7
        return 0

    # Get the assigned BUCKET DISTANCE (in Light Years)
    bucket_key = round(abs(x_plot_position), 1)
    assigned_ly_distance = BUCKET_LY_DISTANCES.get(bucket_key, 300.0)

    # Calculate Base Y-Position using Longitude (l)
    longitude_rad = math.radians(longitude_deg)
    base_y_coord = math.cos(longitude_rad)  # Range: [-1.0, 1.0]

    # Apply Scaling Factor for Correct Spread and Utilization
    MAX_BUCKET_LY_DISTANCE = 300.0
    spread_factor = assigned_ly_distance / MAX_BUCKET_LY_DISTANCE

    # Compensate for negative bias in cos(l) distribution
    MAX_Y_PLOT_LIMIT = 0.55
    MAX_Y_SPREAD_MULTIPLIER = MAX_Y_PLOT_LIMIT * 1.1
    MIN_Y_SPREAD_MULTIPLIER = 0.20
    range_modulation = MAX_Y_SPREAD_MULTIPLIER - MIN_Y_SPREAD_MULTIPLIER

    # Final Spread Multiplier: Linearly interpolates the spread
    final_spread_multiplier = (range_modulation * spread_factor) + MIN_Y_SPREAD_MULTIPLIER

    # Final Y Position
    final_y_position = base_y_coord * final_spread_multiplier

    # Ensure the final result is strictly within the original fixed plot limits
    return min(MAX_Y_PLOT_LIMIT, max(-MAX_Y_PLOT_LIMIT, final_y_position))


def prepare_plot_data(star_list, nudge_dict):
    """
    Calculates both X (distance bucket) and Y (physical spread + nudge)
    coordinates for all stars, centralizing all logic here.
    """
    plot_data = []

    for star in star_list:
        new_star = star.copy()
        star_name = new_star.get("name")

        # Calculate Cartesian Coordinates
        coords = galactic_to_cartesian(star["distance"], star["longitude"], star["latitude"])

        # Calculate X-axis position (Categorize based on X_plot)
        final_x = categorize_x_plot(coords.x_plot)
        new_star["x_plot_position"] = final_x

        # Calculate Y-position (using the new bucket-scaled function)
        base_y_position = calc_y_plot(star, final_x)

        # Apply Nudge and store final Y-position
        nudge_amount = nudge_dict.get(star_name, 0.0)
        final_y = base_y_position + nudge_amount
        new_star["y_plot_position"] = final_y

        plot_data.append(new_star)

    return plot_data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def is_dark_energy(star_name):
    """Check if star is Dark Energy (for special positioning)"""
    return star_name == "Dark Energy"


def get_glyph_position(star_name, x_pos):
    """Get X position for hieroglyphic glyph based on star name"""
    if is_dark_energy(star_name):
        return x_pos + DARK_ENERGY_GLYPH_X_OFFSET
    return x_pos + GLYPH_X_OFFSET


def get_label_position(star_name, glyph_x):
    """Get X position and alignment for label based on star name"""
    if is_dark_energy(star_name):
        return glyph_x + DARK_ENERGY_LABEL_X_OFFSET, "left"
    return glyph_x + LABEL_X_OFFSET, "left"


def get_label_color(star_name, theme):
    """Get label color for star name"""
    if star_name == "Dark Energy":
        return "#FF6B6B"  # Lighter warm red
    elif star_name == "Dark Matter":
        return "#66D9EF"  # Bright cyan
    else:
        return theme["text"]


def make_white_transparent(img):
    """Convert white background in image to transparent alpha channel"""
    if len(img.shape) == 3 and img.shape[-1] == 3:
        import numpy as np

        white_threshold = 0.95
        is_background = np.all(img >= white_threshold, axis=2)
        alpha = np.where(is_background, 0, 1)
        return np.dstack((img, alpha))
    return img


def calculate_glyph_zoom(aspect_ratio, base_zoom=0.035):
    """Calculate zoom level based on glyph aspect ratio"""
    if aspect_ratio > 2.5:
        return base_zoom * 0.4
    elif aspect_ratio > 2.0:
        return base_zoom * 0.5
    elif aspect_ratio > 1.5:
        return base_zoom * 0.65
    elif aspect_ratio > 1.3:
        return base_zoom * 0.8
    return base_zoom


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


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================


def plot_star_hieroglyph(ax, star, all_stars, theme):
    """Enhanced star-hieroglyph plotting with two-line label layout"""

    # Use the pre-calculated positions directly
    x_pos = star["x_plot_position"]
    y_pos = star["y_plot_position"]

    size = STAR_SIZE_OVERRIDES.get(star["name"], 35)

    # Star background rendering
    if star["name"] == "Dark Energy":
        pass  # Dark Energy has no background
    elif star["name"] == "Sagittarius A*" or "Dark" in star["name"] or star["egyptian_name"] == "Nut/Sky":
        # Special rendering for black holes and cosmic entities
        inner_edge_color = (
            "#87CEEB"  # light sky blue for Nut
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
        # Special rendering for Sun
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
        # Standard star rendering
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

    # Glyph positioning
    glyph_x = get_glyph_position(star["name"], x_pos)

    # Render PNG hieroglyph
    glyph_rendered = False
    if glyph_path := find_stellar_png(star["gardiner"]):
        try:
            img = plt.imread(str(glyph_path))
            height, width = img.shape[0], img.shape[1]
            aspect_ratio = height / width

            # Make white background transparent
            img = make_white_transparent(img)

            # Determine zoom level
            glyph_filename = glyph_path.name.replace("US22", "").replace(".png", "")
            if glyph_filename in GLYPH_ZOOM_OVERRIDES:
                base_zoom = GLYPH_ZOOM_OVERRIDES[glyph_filename]
            else:
                base_zoom = calculate_glyph_zoom(aspect_ratio)

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
    label_x, label_ha = get_label_position(star["name"], glyph_x)

    # Line 1: Egyptian name in white
    egyptian_y = y_pos + EGYPTIAN_NAME_Y_OFFSET
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

    # Line 2: Star name with special colors for Dark Matter/Energy
    star_label = star["name"]
    label_color = get_label_color(star["name"], theme)
    star_y = y_pos + STAR_NAME_Y_OFFSET

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


def setup_hieroglyphic_plot(ax, theme):
    """Configure plot appearance with Egyptian astronomical theme"""
    # X-limit adjusted to the max bucket of 2.5
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-0.65, 0.65)

    # Remove tick marks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add vertical grid lines
    for x_val in X_TICKS:
        if x_val == 0:
            ax.axvline(x=x_val, color="#FFD700", alpha=0.8, linestyle="--", linewidth=0.75)
        else:
            ax.axvline(x=x_val, color=theme["grid"], alpha=0.45, linestyle="--", linewidth=0.45)

    # Curved arrow for cosmic navigation
    arrow = FancyArrowPatch(
        (-1.5, -0.60),
        (1.5, -0.60),
        connectionstyle="arc3,rad=0.05",
        arrowstyle="<->",
        mutation_scale=20,
        color="#FFD700",
        alpha=0.6,
        linewidth=1,
        linestyle="--",
    )
    ax.add_patch(arrow)


def create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size="A3"):
    """Create Egyptian hieroglyphic star map with configurable paper sizes"""

    current_theme = THEMES["dark" if dark_mode else "light"]
    figsize = PAPER_DIMENSIONS.get(paper_size, PAPER_DIMENSIONS["A3"])

    fig, ax = plt.subplots(figsize=figsize, facecolor=current_theme["background"])
    ax.set_facecolor(current_theme["background"])

    # Watermark - diagonal across center
    ax.text(
        0,
        0,  # Centered
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

    # Prepare the data with all calculated positions
    plot_ready_stars = prepare_plot_data(STAR_HIEROGLYPHS, MANUAL_NUDGES)

    # Plot all star-hieroglyph pairs
    for star in plot_ready_stars:
        plot_star_hieroglyph(ax, star, STAR_HIEROGLYPHS, current_theme)

    # Add Galactic Center label above Dark Matter/Dark Energy cluster
    gc_y_position = 0.62
    ax.text(
        0,
        gc_y_position,
        "Galactic Center",
        ha="center",
        va="center",
        fontsize=10,
        color="#FFD700",
        weight="bold",
        zorder=5,
    )

    setup_hieroglyphic_plot(ax, current_theme)

    # Remove plot borders
    for spine in ax.spines.values():
        spine.set_visible(False)

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


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    create_hieroglyphic_cosmos_plot(dark_mode=True, paper_size="A3")
