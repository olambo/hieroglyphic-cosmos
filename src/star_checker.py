"""
SIMBAD Coordinate Verification for Hieroglyph-Cosmos
Queries SIMBAD for accurate star coordinates and converts to galactic system
"""

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from star_glyphs import STAR_HIEROGLYPHS


# Configure SIMBAD to return coordinates
custom_simbad = Simbad()
custom_simbad.add_votable_fields("ra", "dec", "plx")


def query_star_coordinates(star_name):
    """Query SIMBAD for a star and return galactic coordinates"""
    try:
        # Query SIMBAD
        result = custom_simbad.query_object(star_name)

        if result is None:
            return None, f"Star '{star_name}' not found in SIMBAD"

        # Get RA/Dec - SIMBAD returns them as strings in format "HH MM SS.SS" and "+DD MM SS.S"
        ra_str = result["RA"][0]
        dec_str = result["DEC"][0]
        # Get RA/Dec - SIMBAD returns them as strings in format "HH MM SS.SS" and "+DD MM SS.S"
        ra_str = result["RA"][0]
        dec_str = result["DEC"][0]

        # Convert to SkyCoord (it handles the sexagesimal format)
        coord = SkyCoord(
            ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg), frame="icrs"
        )
        galactic = coord.galactic

        # Try to get parallax for distance estimate
        plx = (
            result["PLX_VALUE"][0]
            if "PLX_VALUE" in result.colnames and result["PLX_VALUE"][0]
            else None
        )
        distance = None
        if plx and plx > 0:
            distance = round(
                1000.0 / plx, 2
            )  # Convert parallax (mas) to distance (ly approximation)

        return {
            "ra": coord.ra.deg,
            "dec": coord.dec.deg,
            "longitude": round(galactic.l.deg, 2),
            "latitude": round(galactic.b.deg, 2),
            "distance": distance,
        }, None

    except Exception as e:
        return None, f"Error querying '{star_name}': {str(e)}"


def verify_all_coordinates():
    """Verify coordinates for all stars in STAR_HIEROGLYPHS"""
    results = []
    errors = []

    # Skip special non-stellar entries
    skip_names = ["Dark Energy", "Dark Matter", "Milky Way Rotation"]

    stars_to_check = [s for s in STAR_HIEROGLYPHS if s["name"] not in skip_names]

    print(f"Verifying coordinates for {len(stars_to_check)} stars...")
    print("=" * 70)

    for i, star in enumerate(stars_to_check, 1):
        star_name = star["name"]
        print(f"\n[{i}/{len(stars_to_check)}] Querying {star_name}...", end=" ")

        coords, error = query_star_coordinates(star_name)

        if coords:
            print("✓")

            # Compare with current values
            old_lon = star["longitude"]
            old_lat = star["latitude"]
            new_lon = coords["longitude"]
            new_lat = coords["latitude"]

            lon_diff = abs(new_lon - old_lon)
            lat_diff = abs(new_lat - old_lat)

            result = {
                "name": star_name,
                "old_coords": (old_lon, old_lat),
                "new_coords": (new_lon, new_lat),
                "difference": (round(lon_diff, 2), round(lat_diff, 2)),
                "significant_change": lon_diff > 5 or lat_diff > 5,
            }

            if coords["distance"]:
                result["simbad_distance"] = round(coords["distance"], 2)
                result["current_distance"] = star["distance"]

            results.append(result)

            if result["significant_change"]:
                print(f"   ⚠️  Large change: Δlon={lon_diff:.1f}°, Δlat={lat_diff:.1f}°")
        else:
            print("✗")
            print(f"   Error: {error}")
            errors.append({"name": star_name, "error": error})

        # Be nice to SIMBAD servers
        time.sleep(0.5)

    return results, errors


def print_summary(results, errors):
    """Print summary of coordinate verification"""
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    if errors:
        print(f"\n❌ {len(errors)} stars failed:")
        for err in errors:
            print(f"   - {err['name']}: {err['error']}")

    significant_changes = [r for r in results if r["significant_change"]]
    if significant_changes:
        print(
            f"\n⚠️  {len(significant_changes)} stars have significant coordinate changes (>5°):"
        )
        for r in significant_changes:
            print(
                f"   - {r['name']}: "
                f"Δlon={r['difference'][0]}°, Δlat={r['difference'][1]}°"
            )

    print(f"\n✓ {len(results)} stars successfully verified")
    print(
        f"✓ {len([r for r in results if not r['significant_change']])} "
        f"stars have accurate coordinates (<5° difference)"
    )


def generate_updated_code(results):
    """Generate updated STAR_HIEROGLYPHS code with verified coordinates"""
    print("\n" + "=" * 70)
    print("UPDATED COORDINATES")
    print("=" * 70)
    print("\nUpdated star entries (copy these into star_hieroglyphs.py):\n")

    for result in results:
        if result["significant_change"]:
            name = result["name"]
            new_lon, new_lat = result["new_coords"]
            print(f"    # {name}: longitude={new_lon}, latitude={new_lat}")


if __name__ == "__main__":
    print("HIEROGLYPH-COSMOS: SIMBAD Coordinate Verification")
    print("=" * 70)

    results, errors = verify_all_coordinates()
    print_summary(results, errors)

    if results:
        # Ask if user wants to see updated coordinates
        print("\n" + "=" * 70)
        response = input("\nGenerate updated coordinate code? (y/n): ")
        if response.lower() == "y":
            generate_updated_code(results)

    print("\n✨ Verification complete!")
