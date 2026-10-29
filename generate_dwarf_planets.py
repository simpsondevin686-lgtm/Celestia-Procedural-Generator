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
        
        # 1. Orbital Distribution
        pop = random.random()
        if pop < 0.70:
            sma_au = random.uniform(39.0, 48.0)
        elif pop < 0.90:
            sma_au = random.uniform(48.0, 150.0)
        else:
            sma_au = random.choice([39.4, 47.8]) + random.uniform(-0.5, 0.5)
            
        period_years = math.sqrt((sma_au**3) / 1.0)
        period_days = period_years * 365.25
        
        sigma_e = 0.04
        ecc = sigma_e * math.sqrt(-2 * math.log(1.0 - random.random()))
        if ecc > 0.4: ecc = 0.4
        
        inc = random.gauss(0, 8)
        
        # 2. Size Distribution
        u = random.random() 
        q = 3.5
        r_min, r_max = 50.0, 1500.0
        radius_km = ( (r_max**(1-q) - r_min**(1-q)) * u + r_min**(1-q) ) ** (1/(1-q))
        
        # 3. Density & Mass
        density_g_cm3 = random.uniform(0.5, 2.0)
        density_kg_km3 = density_g_cm3 * 1e12
        vol_km3 = (4/3) * math.pi * (radius_km**3)
        mass_kg = vol_km3 * density_kg_km3
        
        # 4. Rotation
        if radius_km < 100:
            rot_hours = random.uniform(0.5, 12.0)
        else:
            rot_hours = random.uniform(3.0, 48.0)
            
        omega = (2 * math.pi) / (rot_hours * 3600)
        R_m = radius_km * 1000
        omega_crit = math.sqrt((G * mass_kg) / (R_m ** 3))
        
        ratio = min(omega / omega_crit, 0.95) 
        flattening = 0.42 * (ratio ** 2)
        
        z_km = int(radius_km * (1 - flattening))
        if z_km < 1: z_km = 1
        semi_axes = f"[ {int(radius_km)} {int(radius_km)} {z_km} ]"
        
        obj_class = "dwarfplanet" if radius_km >= 400 else "asteroid"
        
        pool = rocky if rocky else unknown
        texture = random.choice(pool) if pool else "asteroid.jpg"
        
        geom = random.uniform(0.05, 0.30)
        phase_integral = random.uniform(1.2, 1.8)
        bond = min(0.95, geom * phase_integral)

        orbit = f"""    EllipticalOrbit
    {{
        Epoch 2451545.0
        Period {period_days:.2f}
        SemiMajorAxis {sma_au:.3f}
        Eccentricity {ecc:.3f}
        Inclination {inc:.3f}
        AscendingNode {random.uniform(0, 360):.2f}
        ArgOfPericenter {random.uniform(0, 360):.2f}
        MeanAnomaly {random.uniform(0, 360):.2f}
    }}"""

        # 5. Moons
        hill_radius_km = (sma_au * AU / 1000) * (mass_kg / (3 * M_sun))**(1/3)
        max_moon_dist = hill_radius_km * 0.4
        roche_limit = 2.44 * radius_km * (density_g_cm3 / 1.0)**(1/3)
        min_moon_dist = max(radius_km * 1.5, roche_limit)
        
        has_moon = False
        is_barycenter = False
        
        p_moon = 0.2 if radius_km > 500 else 0.02
        
        if min_moon_dist < max_moon_dist and random.random() < p_moon:
            lo_mass_earth = max(1e5 / M_earth, (mass_kg * 0.001) / M_earth)
            hi_mass_earth = (mass_kg * 0.10) / M_earth
            
            if lo_mass_earth < hi_mass_earth:
                has_moon = True
                moon_dist = random.uniform(min_moon_dist, max_moon_dist)
                moon_mass_earth = random.uniform(lo_mass_earth, hi_mass_earth)
                
                moon_vol_km3 = (moon_mass_earth * M_earth) / density_kg_km3
                moon_radius_km = ((3 * moon_vol_km3) / (4 * math.pi)) ** (1/3)
                
                if (moon_mass_earth * M_earth) > (mass_kg * 0.05):
                    is_barycenter = True
                    
                moon_period_seconds = 2 * math.pi * math.sqrt(((moon_dist * 1000)**3) / (G * (mass_kg + moon_mass_earth * M_earth)))
                moon_period_days = moon_period_seconds / 86400
                moon_rot_hours = moon_period_days * 24
                
                moon_omega = (2 * math.pi) / (moon_rot_hours * 3600)
                moon_omega_crit = math.sqrt((G * moon_mass_earth * M_earth) / ((moon_radius_km * 1000) ** 3))
                moon_ratio = min(moon_omega / moon_omega_crit, 0.95)
                moon_flattening = 0.42 * (moon_ratio ** 2)
                
                moon_z = int(moon_radius_km * (1 - moon_flattening))
                if moon_z < 1: moon_z = 1
                moon_semi_axes = f"[ {int(moon_radius_km)} {int(moon_radius_km)} {moon_z} ]"
                moon_texture = random.choice(pool) if pool else "asteroid.jpg"
                
                moon_geom = random.uniform(0.05, 0.35)
                moon_bond = min(0.95, moon_geom * random.uniform(1.2, 1.8))

        # --- BUILD SSC ---
        if is_barycenter and has_moon:
            # ReferencePoint at the top
            ssc_content.append(f"""
ReferencePoint "{name} System" "Sol"
{{
{orbit}
    Visible true
    Clickable true
}}
""")
            # Dwarf Planet
            mesh_tag = 'Mesh "roughsphere.cms"' if obj_class == "asteroid" else ''
            ssc_content.append(f"""
"{name}:Procedural {name}" "Sol/{name} System"
{{
    Class "{obj_class}"
    {mesh_tag}
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
    
    GeomAlbedo {geom:.3f}
    BondAlbedo {bond:.3f}
}}
""")
            # Moon
            moon_class = "minormoon" if moon_radius_km < 200 else "moon"
            moon_mesh = 'Mesh "roughsphere.cms"' if moon_class == "minormoon" else ''
            ssc_content.append(f"""
"{name} Moon:Procedural {name} I" "Sol/{name}"
{{
    Class "{moon_class}"
    {moon_mesh}
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
        EquatorJ2000 {{ Center "Sol/{name} System" }}
    }}
    
    UniformRotation
    {{
        Period {moon_rot_hours:.2f}
    }}
    
    GeomAlbedo {moon_geom:.3f}
    BondAlbedo {moon_bond:.3f}
}}
""")
        else:
            mesh_tag = 'Mesh "roughsphere.cms"' if obj_class == "asteroid" else ''
            ssc_content.append(f"""
"{name}:Procedural {name}" "Sol"
{{
    Class "{obj_class}"
    {mesh_tag}
    Texture "{texture}"
    SemiAxes {semi_axes}
    Mass<kg> {mass_kg:.5e}

{orbit}

    UniformRotation
    {{
        Period {rot_hours:.2f}
    }}
    
    GeomAlbedo {geom:.3f}
    BondAlbedo {bond:.3f}
}}
""")
            if has_moon:
                moon_class = "minormoon" if moon_radius_km < 200 else "moon"
                moon_mesh = 'Mesh "roughsphere.cms"' if moon_class == "minormoon" else ''
                ssc_content.append(f"""
"{name} Moon:Procedural {name} I" "Sol/{name}"
{{
    Class "{moon_class}"
    {moon_mesh}
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
        EquatorJ2000 {{ Center "Sol/{name}" }}
    }}
    
    UniformRotation
    {{
        Period {moon_rot_hours:.3f}
    }}
    
    GeomAlbedo {moon_geom:.3f}
    BondAlbedo {moon_bond:.3f}
}}
""")

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(SSC_FILE, "w") as f: f.write("".join(ssc_content))
        print("Success! Final Dwarf Planet Generation Complete.")
        print(f"Saved to: {SSC_FILE}")
    except Exception as e: print(f"Error writing files: {e}")

if __name__ == "__main__":
    generate_dwarf_objects()
