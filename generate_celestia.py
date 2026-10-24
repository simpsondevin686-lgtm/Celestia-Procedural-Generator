import os
import random
import math

# ==========================================
# CONFIGURATION
# ==========================================
# IMPORTANT: Update this path to match your specific device
BASE_TEXTURE_PATH = "/storage/emulated/0/CelestiaResources26.8.1/CelestiaResources/textures"

# The output folder for Celestia Mobile
OUTPUT_DIR = "/storage/emulated/0/Android/media/space.celestia.mobilecelestia/CelestiaResources/extras"
STC_FILE = os.path.join(OUTPUT_DIR, "procedural_stars.stc")
SSC_FILE = os.path.join(OUTPUT_DIR, "procedural_planets.ssc")

NUM_SYSTEMS = 10000 
MAX_DIST_LY = 5000.0 
SUN_RADIUS_KM = 696340.0

# Added "star" to prevent planets from getting star textures
BLACKLIST = ["sun", "star", "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "moon", "luna", "titan", "europa", "io", "ganymede", "callisto", "triton", "charon", "phobos", "deimos", "ceres", "eris", "haumea", "makemake", "vesta", "pallas", "hygiea"]

# REALISTIC STELLAR DISTRIBUTION (Initial Mass Function)
STELLAR_CLASSES = [
    {"type": "M", "temp": (2500, 3700), "rad": (0.1, 0.6), "mass": (0.08, 0.45), "min_dist": 4.5, "class": "star", "weight": 75.0},
    {"type": "K", "temp": (3700, 5200), "rad": (0.6, 0.9), "mass": (0.45, 0.8), "min_dist": 4.5, "class": "star", "weight": 12.0},
    {"type": "G", "temp": (5200, 6000), "rad": (0.9, 1.1), "mass": (0.8, 1.04), "min_dist": 4.5, "class": "star", "weight": 7.0},
    {"type": "F", "temp": (6000, 7500), "rad": (1.1, 1.4), "mass": (1.04, 1.4), "min_dist": 4.5, "class": "star", "weight": 3.0},
    {"type": "BrownDwarf", "temp": (500, 2500), "rad": (0.09, 0.15), "mass": (0.013, 0.08), "min_dist": 4.5, "class": "star", "weight": 5.0},
    {"type": "A", "temp": (7500, 10000), "rad": (1.4, 1.8), "mass": (1.4, 2.1), "min_dist": 4.5, "class": "star", "weight": 0.5},
    {"type": "RedGiant", "temp": (3000, 5000), "rad": (10.0, 100.0), "mass": (0.8, 8.0), "min_dist": 4.5, "class": "star", "weight": 0.8},
    {"type": "WhiteDwarf", "temp": (8000, 100000), "rad": (0.008, 0.02), "mass": (0.5, 1.4), "min_dist": 100.0, "class": "star", "weight": 1.0},
    {"type": "B", "temp": (10000, 30000), "rad": (1.8, 6.6), "mass": (2.1, 16.0), "min_dist": 4.5, "class": "star", "weight": 0.1},
    {"type": "BlueSupergiant", "temp": (10000, 40000), "rad": (30.0, 500.0), "mass": (10.0, 50.0), "min_dist": 4.5, "class": "star", "weight": 0.05},
    {"type": "NeutronStar", "temp": (600000, 1000000), "rad": (0.000015, 0.00002), "mass": (1.4, 2.1), "min_dist": 100.0, "class": "star", "weight": 0.05},
    {"type": "WolfRayet", "temp": (30000, 200000), "rad": (1.0, 15.0), "mass": (10.0, 25.0), "min_dist": 100.0, "class": "star", "weight": 0.01},
    {"type": "BlackHole", "temp": (0, 0), "rad": (0.00001, 0.0001), "mass": (3.0, 20.0), "min_dist": 100.0, "class": "blackhole", "weight": 0.01},
    {"type": "O", "temp": (30000, 50000), "rad": (6.6, 15.0), "mass": (16.0, 50.0), "min_dist": 4.5, "class": "star", "weight": 0.01}
]

PLANET_TYPES = [
    {"name": "Chthonian Core",   "chance": 3,  "dist": (0.01, 0.1),  "is_gas": False},
    {"name": "Lava World",       "chance": 8,  "dist": (0.01, 0.2),  "is_gas": False},
    {"name": "Hot Mercury",      "chance": 8,  "dist": (0.1, 0.4),   "is_gas": False},
    {"name": "Venusian",         "chance": 10, "dist": (0.4, 0.8),   "is_gas": False},
    {"name": "Temperate Rocky",  "chance": 10, "dist": (0.8, 1.5),   "is_gas": False},
    {"name": "Ocean World",      "chance": 5,  "dist": (0.8, 1.5),   "is_gas": False},
    {"name": "Super-Earth",      "chance": 8,  "dist": (0.5, 2.0),   "is_gas": False},
    {"name": "Cold Rocky",       "chance": 8,  "dist": (1.5, 4.0),   "is_gas": False},
    {"name": "Ice Planet",       "chance": 10, "dist": (4.0, 20.0),  "is_gas": False},
    {"name": "Mini-Neptune",     "chance": 6,  "dist": (0.5, 5.0),   "is_gas": True},
    {"name": "Ice Giant",        "chance": 5,  "dist": (5.0, 30.0),  "is_gas": True},
    {"name": "Ultra-Hot Jupiter","chance": 3,  "dist": (0.01, 0.1),  "is_gas": True},
    {"name": "Hot Jupiter",      "chance": 6,  "dist": (0.1, 0.8),   "is_gas": True},
    {"name": "Warm Gas Giant",   "chance": 5,  "dist": (0.8, 5.0),   "is_gas": True},
    {"name": "Cold Gas Giant",   "chance": 5,  "dist": (5.0, 30.0),  "is_gas": True}
]

def get_usable_textures():
    gas_pool, rocky_barren, rocky_complex, hot_rocky_pool, unknown_pool = [], [], [], [], []
    icy_rings, dark_rings, lava = [], [], []
    
    if not os.path.exists(BASE_TEXTURE_PATH):
        print(f"WARNING: Texture path not found: {BASE_TEXTURE_PATH}")
        return gas_pool, rocky_barren, rocky_complex, hot_rocky_pool, unknown_pool, icy_rings, dark_rings, lava

    for folder in ["hires", "medres", "lores"]:
        folder_path = os.path.join(BASE_TEXTURE_PATH, folder)
        if not os.path.exists(folder_path): continue
        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(('.jpg', '.png', '.dds', '.jpeg')): continue
            name_lower = filename.lower()
            
            if any(bad in name_lower for bad in BLACKLIST): continue
            
            if "ring" in name_lower: 
                if any(k in name_lower for k in ["saturn", "uranus", "neptune", "icy"]):
                    icy_rings.append(filename)
                else:
                    dark_rings.append(filename) 
                continue
                
            if "night" in name_lower or "lava" in name_lower or "magma" in name_lower or "molten" in name_lower:
                lava.append(filename)
                hot_rocky_pool.append(filename) 
                continue
                
            if any(kw in name_lower for kw in ["exo", "neptunelike", "gas", "giant", "band", "storm", "swirl"]):
                gas_pool.append(filename)
                continue
                
            if any(kw in name_lower for kw in ["venuslike", "hot", "volcan"]):
                hot_rocky_pool.append(filename)
                continue
                
            if any(kw in name_lower for kw in ["terra", "desert", "ocean", "water", "continent", "earthlike"]):
                rocky_complex.append(filename)
                continue
                
            if any(kw in name_lower for kw in ["rock", "crater", "barren", "asteroid", "ice", "frozen", "tundra"]):
                rocky_barren.append(filename)
                continue
                
            unknown_pool.append(filename)

    return gas_pool, rocky_barren, rocky_complex, hot_rocky_pool, unknown_pool, icy_rings, dark_rings, lava

def generate_star_system():
    weights = [s["weight"] for s in STELLAR_CLASSES]
    stellar = random.choices(STELLAR_CLASSES, weights=weights, k=1)[0]
    
    s_type = stellar["type"]
    s_class = stellar["class"]
    temp = random.uniform(stellar["temp"][0], stellar["temp"][1])
    radius = random.uniform(stellar["rad"][0], stellar["rad"][1])
    mass = random.uniform(stellar["mass"][0], stellar["mass"][1])
    
    if s_type == "BlackHole":
        abs_mag = 20.0 
    else:
        luminosity = (radius ** 2) * ((temp / 5778.0) ** 4)
        abs_mag = 4.83 - (2.5 * math.log10(luminosity)) if luminosity > 0 else 20.0
    
    min_dist_sirius_pc = 10 ** ((-1.46 - abs_mag + 5) / 5)
    min_dist_sirius_ly = min_dist_sirius_pc * 3.26156
    
    min_d = max(4.5, stellar["min_dist"], min_dist_sirius_ly)
    max_d = max(MAX_DIST_LY, min_d + 100)
    
    u = random.random()
    distance_ly = min_d + (max_d - min_d) * (u ** 3)
    
    ra = random.uniform(0, 360)
    dec = math.degrees(math.asin(random.uniform(-1, 1)))
    
    if s_type in ["O", "B", "A", "WolfRayet", "BlueSupergiant"]: rot_days = random.uniform(1, 10)
    elif s_type in ["F", "G"]: rot_days = random.uniform(10, 30)
    elif s_type in ["K", "M", "RedGiant"]: rot_days = random.uniform(30, 100)
    elif s_type == "WhiteDwarf": rot_days = random.uniform(0.1, 2)
    elif s_type == "NeutronStar": rot_days = random.uniform(0.00001, 0.01)
    elif s_type == "BrownDwarf": rot_days = random.uniform(0.1, 1)
    else: rot_days = random.uniform(0.1, 10)
    
    if s_type == "NeutronStar": spectral_type_str = '"X"'
    elif s_type in ["O", "B", "A", "F", "G", "K", "M"]: spectral_type_str = f'"{s_type}V"'
    else: spectral_type_str = f'"{s_type}"'
        
    radius_km = radius * SUN_RADIUS_KM
    
    star_ssc = f'\n"TEMP_STAR"\n{{\n    Class "{s_class}"\n    RA {ra:.5f}\n    Dec {dec:.5f}\n    Distance {distance_ly:.2f}\n    SpectralType {spectral_type_str}\n    AbsMag {abs_mag:.2f}\n    Radius {radius_km:.0f} \n    Temperature {int(temp)}\n    UniformRotation\n    {{\n        Period<d> {rot_days:.5f}\n    }}\n}}\n'
    return star_ssc, mass, radius, temp, distance_ly

def pick_texture(primary_pool, unknown_pool):
    if not primary_pool and not unknown_pool: return None
    if not primary_pool: return random.choice(unknown_pool)
    if not unknown_pool: return random.choice(primary_pool)
    return random.choice(primary_pool) if random.random() < 0.5 else random.choice(unknown_pool)


def generate_moons(planet_mass_earth, planet_radius_km, distance_au, star_mass_solar, rocky_barren, unknown_pool):
    G = 6.67430e-11
    M_sun = 1.989e30
    M_earth = 5.972e24
    AU = 1.496e8
    
    star_mass_kg = star_mass_solar * M_sun
    planet_mass_kg = planet_mass_earth * M_earth
    planet_dist_m = distance_au * AU * 1000
    
    # Planet Density (kg/km^3) for Roche Limit
    vol_km3 = (4/3) * math.pi * (planet_radius_km**3)
    planet_density = planet_mass_kg / vol_km3
    
    # Hill Sphere (in km) - The absolute maximum reach of the planet's gravity
    hill_radius_km = (planet_dist_m / 1000) * (planet_mass_kg / (3 * star_mass_kg))**(1/3)
    
    # Max stable moon distance (approx 40% of Hill sphere) - Prevents the star from pulling them away
    max_moon_dist = hill_radius_km * 0.4
    
    # Roche limit - If a moon is closer than this, it gets ripped apart into a ring
    moon_density = 3e12 # Assuming icy/rocky moon density
    roche_limit = 2.44 * planet_radius_km * (planet_density / moon_density)**(1/3)
    
    min_moon_dist = max(planet_radius_km * 1.5, roche_limit)
    
    # If the stable zone is smaller than the Roche limit, no moons can form
    if min_moon_dist >= max_moon_dist:
        return ""
        
    # Number of moons based on planet mass
    if planet_mass_earth > 50:
        num_moons = random.randint(1, 8) # Gas giants get more moons
    elif planet_mass_earth > 1.0:
        num_moons = random.randint(0, 3) # Rocky planets
    else:
        num_moons = random.randint(0, 1) # Small planets
        
    moons_ssc = ""
    
    for i in range(num_moons):
        dist = random.uniform(min_moon_dist, max_moon_dist)
        
        if planet_mass_earth > 50:
            mass_earth = random.uniform(0.0001, 0.05)
        else:
            mass_earth = random.uniform(0.00001, 0.01)
            
        radius_km = (mass_earth ** 0.3) * 6371
        
        # Kepler's Third Law for Moon Orbit
        period_seconds = 2 * math.pi * math.sqrt(((dist * 1000)**3) / (G * planet_mass_kg))
        period_days = period_seconds / 86400
        
        # Tidal Locking - The moon takes the same time to rotate as it does to orbit
        rot_hours = period_days * 24
        
        # Tidal Squishing (Oblateness)
        omega = (2 * math.pi) / (rot_hours * 3600)
        moon_mass_kg = mass_earth * M_earth
        R_m = radius_km * 1000
        omega_crit = math.sqrt((G * moon_mass_kg) / (R_m ** 3))
        ratio = min(omega / omega_crit, 0.9)
        flattening = 0.73 * (ratio ** 2)
        if flattening > 0.4: flattening = 0.4
        
        semi_axes = f"[ {int(radius_km)} {int(radius_km)} {int(radius_km * (1-flattening))} ]"
        
        # Pick a barren texture for the moon
        pool = rocky_barren if rocky_barren else unknown_pool
        texture = random.choice(pool) if pool else "asteroid.jpg"
        
        # The main loop will replace "TEMP_NAME" with the final planet name
        moon_ssc = f"""
"Moon {i+1}:TEMP_NAME" "TEMP_STAR/TEMP_NAME"
{{
    Class "moon"
    Texture "{texture}"
    SemiAxes {semi_axes}
    Mass<kg> {moon_mass_kg:.5e}

    EllipticalOrbit
    {{
        Period {period_days:.3f}
        SemiMajorAxis {dist:.0f}
        Eccentricity {random.uniform(0.001, 0.05):.3f}
        Inclination {random.uniform(-5, 5):.2f}
        AscendingNode {random.uniform(0, 360):.2f}
        ArgOfPericenter {random.uniform(0, 360):.2f}
        MeanAnomaly {random.uniform(0, 360):.2f}
    }}
    
    OrbitFrame
    {{
        EquatorJ2000 {{ Center "TEMP_STAR/TEMP_NAME" }}
    }}
    
    UniformRotation
    {{
        Period {rot_hours:.3f}
    }}
    
    GeomAlbedo {random.uniform(0.05, 0.3):.3f}
    BondAlbedo {random.uniform(0.05, 0.3):.3f}
}}
"""
        moons_ssc += moon_ssc
        
    return moons_ssc

def generate_planet_data(star_mass, star_radius, star_temp, gas_pool, rocky_barren, rocky_complex, hot_rocky_pool, unknown_pool, icy_rings, dark_rings, lava):
    chosen_type = random.choices(PLANET_TYPES, weights=[p["chance"] for p in PLANET_TYPES], k=1)[0]
    is_gas = chosen_type["is_gas"]
    ptype = chosen_type["name"]
    
    dist_min = max(chosen_type["dist"][0], 0.0001)
    distance_au = random.uniform(dist_min, chosen_type["dist"][1])
    
    r_star_au = star_radius * 0.00465
    albedo = random.uniform(0.05, 0.6)
    
    if star_temp > 0 and r_star_au > 0:
        t_eq_k = star_temp * math.sqrt(r_star_au / (2 * distance_au)) * ((1 - albedo)**0.25)
        t_eq_f = (t_eq_k - 273.15) * 9/5 + 32
    else:
        t_eq_f = -450

    if is_gas:
        if ptype == "Ultra-Hot Jupiter":
            mass_earth = random.uniform(300, 1000); radius_earth = random.uniform(13.0, 18.0); primary_pool = gas_pool
        elif ptype == "Hot Jupiter":
            mass_earth = random.uniform(100, 800); radius_earth = random.uniform(10.0, 14.0); primary_pool = gas_pool
        elif ptype == "Mini-Neptune":
            mass_earth = random.uniform(5, 20); radius_earth = random.uniform(2.0, 4.0); primary_pool = gas_pool if gas_pool else rocky_complex
        elif ptype == "Ice Giant":
            mass_earth = random.uniform(10, 50); radius_earth = random.uniform(3.5, 6.0); primary_pool = gas_pool
        else: 
            mass_earth = random.uniform(50, 400); radius_earth = random.uniform(8.0, 12.0); primary_pool = gas_pool
        radius_km = radius_earth * 6371
    else:
        if ptype == "Chthonian Core":
            mass_earth = random.uniform(5, 20); radius_earth = random.uniform(1.0, 2.0); primary_pool = hot_rocky_pool
        elif ptype == "Lava World":
            mass_earth = random.uniform(0.5, 3.0); radius_earth = random.uniform(0.8, 1.3); primary_pool = hot_rocky_pool
        elif ptype == "Hot Mercury":
            mass_earth = random.uniform(0.05, 0.5); radius_earth = random.uniform(0.3, 0.8); primary_pool = hot_rocky_pool if hot_rocky_pool else rocky_barren
        elif ptype == "Venusian":
            mass_earth = random.uniform(0.5, 1.5); radius_earth = random.uniform(0.8, 1.1); primary_pool = hot_rocky_pool
        elif ptype == "Ocean World":
            mass_earth = random.uniform(1.0, 5.0); radius_earth = random.uniform(1.0, 1.6); primary_pool = rocky_complex
        elif ptype == "Super-Earth":
            mass_earth = random.uniform(2.0, 10.0); radius_earth = random.uniform(1.2, 2.0); primary_pool = rocky_complex
        else: 
            mass_earth = random.uniform(0.1, 2.0); radius_earth = random.uniform(0.5, 1.2); primary_pool = rocky_complex if mass_earth > 0.8 else rocky_barren
        radius_km = radius_earth * 6371
        
    mass_kg = mass_earth * 5.972e24

    texture = pick_texture(primary_pool, unknown_pool)
    if not texture: return None

    period_years = math.sqrt((distance_au**3) / star_mass) if star_mass > 0 else 100
    period_days = period_years * 365.25
    lock_dist = 0.5 * (star_mass ** 0.33) 
    
    if distance_au < (lock_dist * 0.7):
        rotation_hours = period_days * 24 
    elif distance_au < lock_dist:
        resonance = random.choice([1.5, 2.0, 2.5])
        rotation_hours = (period_days * 24) / resonance
    else:
        if is_gas: rotation_hours = random.uniform(8, 22)
        else: rotation_hours = random.uniform(10, 60) if random.random() > 0.05 else random.uniform(1000, 5000)

    G = 6.67430e-11
    R_m = radius_km * 1000
    omega = (2 * math.pi) / (rotation_hours * 3600)
    omega_crit = math.sqrt((G * mass_kg) / (R_m ** 3))
    ratio = min(omega / omega_crit, 0.9) 
    flattening = 0.73 * (ratio ** 2)
    if flattening > 0.45: flattening = 0.45
    if flattening < 0: flattening = 0
    semi_axes = f"[ {int(radius_km)} {int(radius_km)} {int(radius_km * (1-flattening))} ]"

    has_atmosphere = False
    atm_height, rayleigh, mie_scale, mie_coeff = 0, "[ 0 0 0 ]", 20, 0.0001
    mass_factor = mass_earth ** 0.5 

    if is_gas or ptype in ["Venusian", "Mini-Neptune"]:
        has_atmosphere = True
        if ptype == "Mini-Neptune":
            atm_height = random.uniform(500, 1500); rayleigh = f"[ 0.001 0.003 0.005 ]"
        elif ptype in ["Ultra-Hot Jupiter", "Hot Jupiter"]:
            atm_height = random.uniform(3000, 10000) if t_eq_f > 900 else random.uniform(2000, 5000)
            rayleigh = f"[ 0.005 0.002 0.001 ]" if t_eq_f > 900 else f"[ 0.002 0.002 0.004 ]"
        else:
            atm_height = random.uniform(1000, 3000); rayleigh = f"[ 0.001 0.003 0.004 ]"
    else:
        if mass_earth > 0.05:
            if t_eq_f > 1800 and mass_earth < 2.0: 
                has_atmosphere = False
            else:
                has_atmosphere = True
                if t_eq_f > 700: 
                    atm_height = random.uniform(100, 800) * mass_factor
                    rayleigh = f"[ {0.006*mass_factor:.4f} {0.002*mass_factor:.4f} {0.0005*mass_factor:.4f} ]"
                    mie_coeff = 0.0003 * mass_factor
                elif t_eq_f > 200: 
                    atm_height = random.uniform(50, 120) * mass_factor
                    rayleigh = f"[ {0.001*mass_factor:.4f} {0.002*mass_factor:.4f} {0.005*mass_factor:.4f} ]"
                    mie_coeff = 0.00015 * mass_factor
                else: 
                    atm_height = random.uniform(10, 60) * mass_factor
                    rayleigh = f"[ {0.001*mass_factor:.4f} {0.003*mass_factor:.4f} {0.003*mass_factor:.4f} ]"
                    mie_coeff = 0.0001 * mass_factor

    has_rings = False
    if is_gas and ptype != "Ultra-Hot Jupiter":
        if ptype == "Hot Jupiter": has_rings = random.random() < 0.1
        elif ptype == "Warm Gas Giant": has_rings = random.random() < 0.4
        elif ptype in ["Cold Gas Giant", "Ice Giant"]: has_rings = random.random() < 0.8
    elif not is_gas: has_rings = random.random() < 0.05

    night_texture_str = ""
    if t_eq_f > 900: 
        if lava:
            night_tex = random.choice(lava)
            night_texture_str = f'\n    NightTexture "{night_tex}"'
        elif unknown_pool:
            night_tex = random.choice(unknown_pool)
            night_texture_str = f'\n    NightTexture "{night_tex}"'

    planet_ssc = f'\n"TEMP_NAME" "TEMP_STAR"\n{{\n    Class "planet"\n    Texture "{texture}"{night_texture_str}\n    Color [ {random.uniform(0.8, 1.0):.2f} {random.uniform(0.8, 1.0):.2f} {random.uniform(0.8, 1.0):.2f} ]\n    SemiAxes {semi_axes}\n    Mass<kg> {mass_kg:.5e}\n    \n    EllipticalOrbit\n    {{\n        Period {period_days:.2f}\n        SemiMajorAxis {distance_au:.5f}\n        Eccentricity {random.uniform(0.01, 0.15):.3f}\n        Inclination {random.uniform(-5, 5):.3f}\n        AscendingNode {random.uniform(0, 360):.2f}\n        ArgOfPericenter {random.uniform(0, 360):.2f}\n        MeanAnomaly {random.uniform(0, 360):.2f}\n    }}\n'

    if has_atmosphere:
        planet_ssc += f'    \n    Atmosphere\n    {{\n        Height {int(atm_height)}\n        Mie {mie_coeff:.6f}\n        MieScaleHeight {mie_scale}\n        MieHGAnisotropy 0.15\n        Rayleigh {rayleigh}\n    }}\n'

    planet_ssc += f'    \n    UniformRotation\n    {{\n        Period {rotation_hours:.2f}\n        Inclination {random.uniform(-20, 20):.2f}\n    }}\n    \n    GeomAlbedo {albedo:.3f}\n    BondAlbedo {random.uniform(0.05, 0.6):.3f}\n'

    if has_rings:
        if t_eq_f < 32:
            ring_pool = icy_rings if icy_rings else dark_rings
        else:
            ring_pool = dark_rings if dark_rings else icy_rings
            
        if ring_pool:
            ring_texture = random.choice(ring_pool)
            inner_ring = radius_km * random.uniform(1.2, 1.5)
            outer_ring = inner_ring + random.uniform(10000, 60000)
            planet_ssc += f'    \n    Rings\n    {{\n        Inner {int(inner_ring)}\n        Outer {int(outer_ring)}\n        Texture "{ring_texture}"\n    }}\n'
            
    planet_ssc += "}\n"
    
        # Inject Moons
    moons_ssc = generate_moons(mass_earth, radius_km, distance_au, star_mass, rocky_barren, unknown_pool)
    planet_ssc += moons_ssc
    
    return {"data": planet_ssc, "dist": distance_au}

def main():
    print("Scanning textures...")
    gas, rocky_barren, rocky_complex, hot_rocky, unknown, icy_rings, dark_rings, lava = get_usable_textures()
    if not rocky_barren and not gas and not unknown: 
        print("Error: No valid textures found. Check your BASE_TEXTURE_PATH.")
        return
    
    print(f"Found: {len(icy_rings)} Icy Rings, {len(dark_rings)} Dark/Rocky Rings")
    print(f"Generating {NUM_SYSTEMS} systems...")
    
    all_systems = []
    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
    
    for i in range(NUM_SYSTEMS):
        if i > 0 and i % 1000 == 0: print(f"Generated {i} systems...")
        
        star_data, star_mass, star_radius, star_temp, distance_ly = generate_star_system()
        
        system_planets = []
        for p in range(random.randint(2, 9)):
            p_data = generate_planet_data(star_mass, star_radius, star_temp, gas, rocky_barren, rocky_complex, hot_rocky, unknown, icy_rings, dark_rings, lava)
            if p_data: system_planets.append(p_data)
                
        system_planets.sort(key=lambda x: x["dist"])
        
        all_systems.append({
            "distance": distance_ly,
            "star_data": star_data,
            "planets": system_planets
        })

    print("Sorting all systems by distance from Earth...")
    all_systems.sort(key=lambda x: x["distance"])
    
    print("Assigning Catalog Names (FKE-10001 and up) and writing to file...")
    stc_content = []
    ssc_content = []
    
    for index, system in enumerate(all_systems):
        star_name = f"FKE-{10001 + index}"
        
        final_star_data = system["star_data"].replace('"TEMP_STAR"', f'"{star_name}"')
        stc_content.append(final_star_data)
        
        for p_index, planet in enumerate(system["planets"]):
            roman_numeral = romans[p_index] if p_index < len(romans) else str(p_index + 1)
            planet_name = f"{star_name} {roman_numeral}"
            planet_str = planet["data"].replace('"TEMP_STAR"', f'"{star_name}"').replace('"TEMP_NAME"', f'"{planet_name}"')
            planet_str = planet_str.replace('"TEMP_STAR/TEMP_NAME"', f'"{star_name}/{planet_name}"')
            ssc_content.append(planet_str)

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(STC_FILE, "w") as f: f.write("".join(stc_content))
        with open(SSC_FILE, "w") as f: f.write("".join(ssc_content))
        print("Success! Generation Complete.")
    except Exception as e: print(f"Error writing files: {e}")

if __name__ == "__main__":
    main()
