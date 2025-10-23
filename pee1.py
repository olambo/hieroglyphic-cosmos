from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.simbad import Simbad
import warnings
warnings.filterwarnings('ignore')

# Paste your STAR_HIEROGLYPHS_SIMBAD here
STAR_HIEROGLYPHS_SIMBAD = [
    {
        "name": "Van Maanen",
        "simbad_name": "GJ 35",
        "distance": 14,
        "longitude": 70.0,
        "latitude": -34.0,
        "size": 20,
        "hieroglyph": "𓂓",
        "egyptian_name": "Ka",
        "gardiner": "D28",
        "description": "Vital Essence",
        "color": "#FFFFFF",
    },
]

def get_star_data(name, simbad_name):
    """Get corrected coordinates and distance from SIMBAD"""
    query_name = simbad_name if simbad_name else name

    try:
        # Get coordinates
        c = SkyCoord.from_name(query_name, frame='galactic')

        # Get distance from SIMBAD if available
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('distance')
        result = custom_simbad.query_object(query_name)

        distance = None
        if result and 'Distance_distance' in result.colnames:
            dist_value = result['Distance_distance'][0]
            if dist_value and not str(dist_value).lower() == 'nan':
                distance = float(dist_value)

        return {
            'longitude': round(c.l.degree, 2),
            'latitude': round(c.b.degree, 2),
            'distance': distance,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'longitude': None,
            'latitude': None,
            'distance': None,
            'success': False,
            'error': str(e)
        }

def update_coordinates():
    """Update all star coordinates with SIMBAD data"""
    updated = []
    total = len(STAR_HIEROGLYPHS_SIMBAD)

    print(f"\nFetching correct coordinates for {total} stars...\n")

    for i, star in enumerate(STAR_HIEROGLYPHS_SIMBAD, 1):
        name = star['name']
        simbad_name = star.get('simbad_name', '')

        print(f"[{i}/{total}] {name}...", end=" ")

        # Skip special non-stars
        if name in ['Dark Energy', 'Dark Matter', 'Milky Way Rotation', 'Sol']:
            print("SKIP (not a real star)")
            updated.append(star)
            continue

        # Get correct data
        data = get_star_data(name, simbad_name)

        if data['success']:
            star_copy = star.copy()

            # Show changes
            old_lon = star['longitude']
            old_lat = star['latitude']
            old_dist = star['distance']

            new_lon = data['longitude']
            new_lat = data['latitude']
            new_dist = data['distance'] if data['distance'] else old_dist

            lon_diff = abs(new_lon - old_lon) if new_lon else 0
            lat_diff = abs(new_lat - old_lat) if new_lat else 0

            if lon_diff > 1 or lat_diff > 1:
                print(f"✓ CHANGED (Δlon={lon_diff:.2f}°, Δlat={lat_diff:.2f}°)")
            else:
                print(f"✓ OK (minimal change)")

            # Update values
            star_copy['longitude'] = new_lon
            star_copy['latitude'] = new_lat
            star_copy['distance'] = new_dist

            updated.append(star_copy)
        else:
            print(f"✗ FAILED: {data['error'][:50]}")
            updated.append(star)

    print(f"\n✓ Processed all {total} stars!\n")
    return updated

def print_star(star, is_last=False):
    """Print a single star dict"""
    print("    {")

    # Define field order
    field_order = ['name', 'simbad_name', 'distance', 'longitude', 'latitude',
                   'size', 'hieroglyph', 'egyptian_name', 'gardiner', 'description', 'color']

    # Print in order
    for key in field_order:
        if key in star:
            value = star[key]
            if isinstance(value, str):
                print(f'        "{key}": "{value}",')
            else:
                print(f'        "{key}": {value},')

    # Print any remaining fields not in order
    for key, value in star.items():
        if key not in field_order:
            if isinstance(value, str):
                print(f'        "{key}": "{value}",')
            else:
                print(f'        "{key}": {value},')

    if is_last:
        print("    }")
    else:
        print("    },")

# Update coordinates
updated_stars = update_coordinates()

print("=" * 80)
print("UPDATED DATASET WITH CORRECT COORDINATES:")
print("=" * 80)
print("\nSTAR_HIEROGLYPHS_CORRECTED = [")

for i, star in enumerate(updated_stars):
    print_star(star, is_last=(i == len(updated_stars) - 1))

print("]")

print("\n" + "=" * 80)
print("✓ Done! Copy the STAR_HIEROGLYPHS_CORRECTED dataset above.")
print("=" * 80)
