from astroquery.utils.tap.core import Tap
import pandas as pd
import numpy as np

tap = Tap(url="https://simbad.u-strasbg.fr/simbad/sim-tap")

lon_min, lon_max = 0, 90

query = f"""
SELECT
  main_id,
  RA,
  DEC,
  COORD1(galactic(ra, dec)) AS glon,
  COORD2(galactic(ra, dec)) AS glat,
  plx_value
FROM basic
WHERE otype = 'Star'
AND main_id NOT LIKE '[%'       -- exclude unnamed objects
AND COORD1(galactic(ra, dec)) BETWEEN {lon_min} AND {lon_max}
"""

job = tap.launch_job(query)
results = job.get_results()
df = results.to_pandas()

# Convert parallax (milliarcseconds) to distance in parsecs
# distance_pc = 1000 / parallax (mas)
df["distance_pc"] = 1000 / df["plx_value"]
df["distance_ly"] = df["distance_pc"] * 3.26156

# Clean up
df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["distance_pc"])
df = df.sort_values("glon").reset_index(drop=True)

print(df[["main_id", "glon", "distance_ly"]].head(20))
