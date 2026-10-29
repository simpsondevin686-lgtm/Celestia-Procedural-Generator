import os
import random
import math

# ==========================================
# CONFIGURATION
# ==========================================
BASE_TEXTURE_PATH = "/storage/emulated/0/CelestiaResources26.8.1/CelestiaResources/textures"
OUTPUT_DIR = "/storage/emulated/0/Android/media/space.celestia.mobilecelestia/CelestiaResources/extras"
SSC_FILE = os.path.join(OUTPUT_DIR, "dwarf_planets.ssc")

NUM_OBJECTS = 5000

BLACKLIST = ["sun", "star", "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "moon", "luna", "titan", "europa", "io", "ganymede", "callisto", "triton", "charon", "phobos", "deimos", "ceres", "eris", "haumea", "makemake", "vesta", "pallas", "hygiea"]

def get_rocky_textures():
    rocky_pool = []
    unknown_pool = []
    
    if not os.path.exists(BASE_TEXTURE_PATH):
        return ["asteroid.jpg"], []

    for folder in ["hires", "medres", "lores"]:
        folder_path = os.path.join(BASE_TEXTURE_PATH, folder)
        if not os.path.exists(folder_path): continue
        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(('.jpg', '.png', '.dds', '.jpeg')): continue
            name_lower = filename.lower()
            
            if any(bad in name_lower for bad in BLACKLIST): continue
            if "ring" in name_lower or "exo" in name_lower or "neptunelike" in name_lower or "gas" in name_lower: continue
            
            if any(kw in name_lower for kw in ["rock", "crater", "barren", "asteroid", "ice", "frozen", "tundra"]):
                rocky_pool.append(filename)
            else:
                unknown_pool.append(filename)

    return rocky_pool, unknown_pool

def generate_dwarf_objects():
    print("Scanning textures for Dwarf Planets...")
    rocky, unknown = get_rocky_textures()
    if not rocky and not unknown:
        print("Error: No rocky textures found.")
        return

    print(f"Generating {NUM_OBJECTS} Dwarf Planets / Asteroids...")
    ssc_content = []
    G = 6.67430e-11
    M_sun = 1.989e30
    M_earth = 5.972e24
    AU = 1.496e11

    for i in range(NUM_OBJECTS):
        if i > 0 and i % 1000 == 0: print(f"Generated {i} objects...")
        
        name = f"DP-{10001 + i}"
        
        # 1. Distances (Outer Solar System / Kuiper Belt)
        sma_au = random.uniform(30.0, 150.0)
        period_years = math.sqrt((sma_au**3) / 1.0) # Assuming 1 Solar Mass
        period_days = period_years * 365.25
        
        # 2. Size (Slightly bigger than Pluto to tiny fragments)
        # Pluto radius is ~1188 km
        radius_km = random.uniform(10.0, 2500.0) 
        
        # 3. Density & Mass
        density_g_cm3 = random.uniform(1.5, 3.5)
        density_kg_km3 = density_g_cm3 * 1e12
        vol_km3 = (4/3) * math.pi * (radius_km**3)
        mass_kg = vol_km3 * density_kg_km3
        
        # 4. Rotation & Squishing
        # Smaller objects can spin extremely fast. 
        if radius_km < 100:
            rot_hours = random.uniform(0.5, 12.0) # Asteroids spin fast
        else:
            rot_hours = random.uniform(3.0, 48.0)
            
        omega = (2 * math.pi) / (rot_hours * 3600)
        R_m = radius_km * 1000
        omega_crit = math.sqrt((G * mass_kg) / (R_m ** 3))
        
        # Dynamic squishing based on real physics
        ratio = min(omega / omega_crit, 0.95) 
        flattening = 0.73 * (ratio ** 2)
        
        # We do not hardcode a max limit, just prevent math errors at breakup
        if flattening > 0.6: flattening = 0.6 
        if flattening < 0: flattening = 0
        
        semi_axes = f"[ {int(radius_km)} {int(radius_km)} {int(radius_km * (1-flattening))} ]"
        
        # Texture
        pool = rocky if rocky else unknown
        texture = random.choice(pool) if pool else "asteroid.jpg"
        
        # Base Orbit
        orbit = f"""    EllipticalOrbit
    {{
        Period {period_days:.2f}
        SemiMajorAxis {sma_au:.3f}
        Eccentricity {random.uniform(0.05, 0.4):.3f}
        Inclination {random.uniform(-30, 30):.3f}
        AscendingNode {random.uniform(0, 360):.2f}
        ArgOfPericenter {random.uniform(0, 360):.2f}
        MeanAnomaly {random.uniform(0, 360):.2f}
    }}"""

        # 5. Check for Moons / Barycenter
        # Hill sphere
        hill_radius_km = (sma_au * AU / 1000) * (mass_kg / (3 * M_sun))**(1/3)
        max_moon_dist = hill_radius_km * 0.4
        roche_limit = 2.44 * radius_km * (density_g_cm3 / 1.0)**(1/3)
        min_moon_dist = max(radius_km * 1.5, roche_limit)
        
        has_moon = False
        is_barycenter = False
        
        if min_moon_dist < max_moon_dist and radius_km > 200:
            if random.random() < 0.3: # 30% chance of having a moon
                has_moon = True
                moon_dist = random.uniform(min_moon_dist, max_moon_dist)
                moon_mass_earth = random.uniform(0.0001, 0.01) if radius_km < 1000 else random.uniform(0.0005, 0.05)
                moon_radius_km = (moon_mass_earth * M_earth / (density_kg_km3 * (4/3) * math.pi))**(1/3)
                
                # Check Barycenter condition: Moon is massive (>10% of planet mass)
                if (moon_mass_earth * M_earth) > (mass_kg * 0.1):
                    is_barycenter = True
                    
                # Moon Orbit
                moon_period_seconds = 2 * math.pi * math.sqrt(((moon_dist * 1000)**3) / (G * (mass_kg + moon_mass_earth * M_earth)))
                moon_period_days = moon_period_seconds / 86400
                moon_rot_hours = moon_period_days * 24 # Tidally locked
                
                # Moon squish
                moon_omega = (2 * math.pi) / (moon_rot_hours * 3600)
                moon_omega_crit = math.sqrt((G * moon_mass_earth * M_earth) / ((moon_radius_km * 1000) ** 3))
                moon_ratio = min(moon_omega / moon_omega_crit, 0.95)
                moon_flattening = 0.73 * (moon_ratio ** 2)
                if moon_flattening > 0.6: moon_flattening = 0.6
                moon_semi_axes = f"[ {int(moon_radius_km)} {int(moon_radius_km)} {int(moon_radius_km * (1-moon_flattening))} ]"
                moon_texture = random.choice(pool) if pool else "asteroid.jpg"

        # --- BUILD SSC ---
        if is_barycenter:
            # Define the Barycenter
            ssc_content.append(f"""
Barycenter "{name} System"
{{
{orbit}
}}
""")
            # Planet orbits barycenter
            ssc_content.append(f"""
"{name}" "{name} System"
{{
    Class "dwarfplanet"
    Texture "{texture}"
    SemiAxes {semi_axes}
    Mass<kg> {mass_kg:.5e}
    
    EllipticalOrbit
    {{
        Period {moon_period_days:.2f}
        SemiMajorAxis {moon_dist * (moon_mass_earth * M_earth) / (mass_kg + moon_mass_earth * M_earth):.0f}
        Eccentricity 0.01
    }}
    
    UniformRotation
    {{
        Period {rot_hours:.2f}
    }}
    
    GeomAlbedo {random.uniform(0.05, 0.3):.3f}
    BondAlbedo {random.uniform(0.05, 0.3):.3f}
}}
""")
            # Moon orbits barycenter
            ssc_content.append(f"""
"{name} Moon" "{name} System"
{{
    Class "moon"
    Texture "{moon_texture}"
    SemiAxes {moon_semi_axes}
    Mass<kg> {moon_mass_earth * M_earth:.5e}
    
    EllipticalOrbit
    {{
        Period {moon_period_days:.2f}
        SemiMajorAxis {moon_dist * (mass_kg) / (mass_kg + moon_mass_earth * M_earth):.0f}
        Eccentricity 0.01
    }}
    
    OrbitFrame
    {{
        EquatorJ2000 {{ Center "{name} System" }}
    }}
    
    UniformRotation
    {{
        Period {moon_rot_hours:.2f}
    }}
    
    GeomAlbedo {random.uniform(0.05, 0.3):.3f}
    BondAlbedo {random.uniform(0.05, 0.3):.3f}
}}
""")
        else:
            # Normal planet
            ssc_content.append(f"""
"{name}" "Sol"
{{
    Class "dwarfplanet"
    Texture "{texture}"
    SemiAxes {semi_axes}
    Mass<kg> {mass_kg:.5e}

{orbit}

    UniformRotation
    {{
        Period {rot_hours:.2f}
    }}
    
    GeomAlbedo {random.uniform(0.05, 0.3):.3f}
    BondAlbedo {random.uniform(0.05, 0.3):.3f}
}}
""")
            # Normal moon
            if has_moon:
                ssc_content.append(f"""
"{name} Moon" "{name}"
{{
    Class "moon"
    Texture "{moon_texture}"
    SemiAxes {moon_semi_axes}
    Mass<kg> {moon_mass_earth * M_earth:.5e}
    
    EllipticalOrbit
    {{
        Period {moon_period_days:.3f}
        SemiMajorAxis {moon_dist:.0f}
        Eccentricity {random.uniform(0.001, 0.05):.3f}
        Inclination {random.uniform(-5, 5):.2f}
        AscendingNode {random.uniform(0, 360):.2f}
        ArgOfPericenter {random.uniform(0, 360):.2f}
        MeanAnomaly {random.uniform(0, 360):.2f}
    }}
    
    OrbitFrame
    {{
        EquatorJ2000 {{ Center "{name}" }}
    }}
    
    UniformRotation
    {{
        Period {moon_rot_hours:.3f}
    }}
    
    GeomAlbedo {random.uniform(0.05, 0.3):.3f}
    BondAlbedo {random.uniform(0.05, 0.3):.3f}
}}
""")

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(SSC_FILE, "w") as f: f.write("".join(ssc_content))
        print("Success! Dwarf Planet Generation Complete.")
        print(f"Saved to: {SSC_FILE}")
    except Exception as e: print(f"Error writing files: {e}")

if __name__ == "__main__":
    generate_dwarf_objects()
