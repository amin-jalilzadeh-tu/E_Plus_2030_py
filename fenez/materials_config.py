# fenez/materials_config.py

import random
from .data_materials_residential import residential_materials_data
from .data_materials_non_residential import non_residential_materials_data
#from .materials_config import material_lookup, pick_val, assign_material_from_lookup
###############################################################################
#  Material lookup dictionary
#  Here you define available material "templates" (with ranges),
#  which your building data references by name.
###############################################################################
material_lookup = {
    "Concrete_200mm": {
        "obj_type": "MATERIAL",
        "Name": "Concrete_200mm",
        "Roughness": "MediumRough",
        "Thickness_range": (0.195, 0.205),
        "Conductivity_range": (1.5, 1.7),
        "Density_range": (2250, 2350),
        "Specific_Heat_range": (850, 950),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    "InsulationBoard_R2": {
        "obj_type": "MATERIAL:NOMASS",
        "Name": "InsulationBoard_R2",
        "Roughness": "MediumRough",
        "Thermal_Resistance_range": (0.34, 0.36),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    "Glazing_Clear_3mm": {
        "obj_type": "WINDOWMATERIAL:GLAZING",
        "Name": "Glazing_Clear_3mm",
        "Optical_Data_Type": "SpectralAverage",
        "Thickness_range": (0.003, 0.003),
        "Solar_Transmittance_range": (0.76, 0.78),
        "Front_Solar_Reflectance_range": (0.07, 0.08),
        "Back_Solar_Reflectance_range": (0.07, 0.08),
        "Visible_Transmittance_range": (0.86, 0.88),
        "Front_Visible_Reflectance_range": (0.06, 0.07),
        "Back_Visible_Reflectance_range": (0.06, 0.07),
        "IR_Transmittance": 0.0,
        "Front_IR_Emissivity_range": (0.84, 0.84),
        "Back_IR_Emissivity_range": (0.84, 0.84),
        "Conductivity_range": (0.95, 1.05),
        "Dirt_Correction_Factor_range": (1.0, 1.0),
        "Solar_Diffusing": "No"
    },

    "Glazing_Clear_3mm_Post": {
        "obj_type": "WINDOWMATERIAL:GLAZING",
        "Name": "Glazing_Clear_3mm_Post",
        "Optical_Data_Type": "SpectralAverage",
        "Thickness_range": (0.003, 0.003),
        "Solar_Transmittance_range": (0.75, 0.75),
        "Front_Solar_Reflectance_range": (0.07, 0.07),
        "Back_Solar_Reflectance_range": (0.07, 0.07),
        "Visible_Transmittance_range": (0.85, 0.85),
        "Front_Visible_Reflectance_range": (0.07, 0.07),
        "Back_Visible_Reflectance_range": (0.07, 0.07),
        "IR_Transmittance": 0.0,
        "Front_IR_Emissivity_range": (0.84, 0.84),
        "Back_IR_Emissivity_range": (0.84, 0.84),
        "Conductivity_range": (1.0, 1.0),
        "Dirt_Correction_Factor_range": (1.0, 1.0),
        "Solar_Diffusing": "No"
    },

    "DoorPanel_Range": {
        "obj_type": "MATERIAL",
        "Name": "DoorPanel_Range",
        "Roughness": "MediumSmooth",
        "Thickness_range": (0.04, 0.05),
        "Conductivity_range": (0.4, 0.5),
        "Density_range": (600, 700),
        "Specific_Heat_range": (1200, 1300),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    # [ADDED] Example new entries for ceiling, roof, ground, etc.
    "Ceiling_Insulation_R3": {
        "obj_type": "MATERIAL",
        "Name": "Ceiling_Insulation_R3",
        "Roughness": "MediumRough",
        "Thickness_range": (0.02, 0.03),
        "Conductivity_range": (0.035, 0.045),
        "Density_range": (20, 25),
        "Specific_Heat_range": (1400, 1500),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    "Roof_Insulation_R5": {
        "obj_type": "MATERIAL",
        "Name": "Roof_Insulation_R5",
        "Roughness": "MediumRough",
        "Thickness_range": (0.04, 0.05),
        "Conductivity_range": (0.03, 0.04),
        "Density_range": (25, 30),
        "Specific_Heat_range": (1400, 1500),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    "AdiabaticWall_Generic": {
        "obj_type": "MATERIAL",
        "Name": "AdiabaticWall_Generic",
        "Roughness": "MediumSmooth",
        "Thickness_range": (0.15, 0.20),
        "Conductivity_range": (0.30, 0.40),
        "Density_range": (200, 300),
        "Specific_Heat_range": (1000, 1100),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },

    "GroundContactFloor_Generic": {
        "obj_type": "MATERIAL",
        "Name": "GroundContactFloor_Generic",
        "Roughness": "MediumRough",
        "Thickness_range": (0.10, 0.12),
        "Conductivity_range": (1.0, 1.2),
        "Density_range": (2100, 2300),
        "Specific_Heat_range": (850, 900),
        "Thermal_Absorptance_range": (0.9, 0.9),
        "Solar_Absorptance_range": (0.7, 0.7),
        "Visible_Absorptance_range": (0.7, 0.7)
    },
}


###############################################################################
#  Residential and Non-residential data are imported from your separate modules
###############################################################################
from .data_materials_residential import residential_materials_data
from .data_materials_non_residential import non_residential_materials_data


def pick_val(rng, strategy="A"):
    """
    Helper to pick a single float from (min,max).
    If rng=(x,x), return x.
    If strategy="A", pick the midpoint. If "B", pick random uniform in the range.
    """
    if rng[0] == rng[1]:
        return rng[0]
    if strategy == "A":
        return (rng[0] + rng[1]) / 2.0
    elif strategy == "B":
        return random.uniform(rng[0], rng[1])
    else:
        # fallback
        return rng[0]


def assign_material_from_lookup(mat_def: dict, strategy="A"):
    """
    Takes a dict from material_lookup, which has fields like "Thickness_range",
    "Conductivity_range", etc. Returns a copy with final numeric picks assigned.
    """
    final_mat = dict(mat_def)  # shallow copy
    obj_type = final_mat["obj_type"].upper()

    if obj_type == "MATERIAL":
        final_mat["Thickness"] = pick_val(final_mat.get("Thickness_range", (0.2, 0.2)), strategy)
        final_mat["Conductivity"] = pick_val(final_mat.get("Conductivity_range", (1.4, 1.4)), strategy)
        final_mat["Density"] = pick_val(final_mat.get("Density_range", (2300, 2300)), strategy)
        final_mat["Specific_Heat"] = pick_val(final_mat.get("Specific_Heat_range", (900, 900)), strategy)
        final_mat["Thermal_Absorptance"] = pick_val(
            final_mat.get("Thermal_Absorptance_range", (0.9, 0.9)), strategy
        )
        final_mat["Solar_Absorptance"] = pick_val(
            final_mat.get("Solar_Absorptance_range", (0.7, 0.7)), strategy
        )
        final_mat["Visible_Absorptance"] = pick_val(
            final_mat.get("Visible_Absorptance_range", (0.7, 0.7)), strategy
        )

    elif obj_type == "MATERIAL:NOMASS":
        final_mat["Thermal_Resistance"] = pick_val(
            final_mat.get("Thermal_Resistance_range", (0.35, 0.35)), strategy
        )
        final_mat["Thermal_Absorptance"] = pick_val(
            final_mat.get("Thermal_Absorptance_range", (0.9, 0.9)), strategy
        )
        final_mat["Solar_Absorptance"] = pick_val(
            final_mat.get("Solar_Absorptance_range", (0.7, 0.7)), strategy
        )
        final_mat["Visible_Absorptance"] = pick_val(
            final_mat.get("Visible_Absorptance_range", (0.7, 0.7)), strategy
        )

    elif obj_type == "WINDOWMATERIAL:GLAZING":
        final_mat["Thickness"] = pick_val(final_mat.get("Thickness_range", (0.003, 0.003)), strategy)
        final_mat["Solar_Transmittance"] = pick_val(
            final_mat.get("Solar_Transmittance_range", (0.76, 0.76)), strategy
        )
        final_mat["Front_Solar_Reflectance"] = pick_val(
            final_mat.get("Front_Solar_Reflectance_range", (0.07, 0.07)), strategy
        )
        final_mat["Back_Solar_Reflectance"] = pick_val(
            final_mat.get("Back_Solar_Reflectance_range", (0.07, 0.07)), strategy
        )
        final_mat["Visible_Transmittance"] = pick_val(
            final_mat.get("Visible_Transmittance_range", (0.86, 0.86)), strategy
        )
        final_mat["Front_Visible_Reflectance"] = pick_val(
            final_mat.get("Front_Visible_Reflectance_range", (0.06, 0.06)), strategy
        )
        final_mat["Back_Visible_Reflectance"] = pick_val(
            final_mat.get("Back_Visible_Reflectance_range", (0.06, 0.06)), strategy
        )
        final_mat["Front_IR_Emissivity"] = pick_val(
            final_mat.get("Front_IR_Emissivity_range", (0.84, 0.84)), strategy
        )
        final_mat["Back_IR_Emissivity"] = pick_val(
            final_mat.get("Back_IR_Emissivity_range", (0.84, 0.84)), strategy
        )
        final_mat["Conductivity"] = pick_val(
            final_mat.get("Conductivity_range", (1.0, 1.0)), strategy
        )
        final_mat["Dirt_Correction_Factor"] = pick_val(
            final_mat.get("Dirt_Correction_Factor_range", (1.0, 1.0)), strategy
        )

    elif obj_type == "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM":
        # e.g. pick UFactor, SHGC, etc., if present in the dictionary
        pass

    return final_mat


def compute_wwr(elements_dict, include_doors=False):
    """
    Compute WWR => (window area) / (external wall area).
    If include_doors=True, add door area to the 'window' portion.
    """
    external_wall_area = 0.0
    # Example: check multiple wall keys if your data has them
    if "solid_wall" in elements_dict:
        external_wall_area += elements_dict["solid_wall"].get("area_m2", 0.0)
    if "exterior_wall" in elements_dict:
        external_wall_area += elements_dict["exterior_wall"].get("area_m2", 0.0)
    if "sloping_flat_roof" in elements_dict:  # or some other roof/wall combos
        pass
    # etc. (add more if your data structure requires)

    window_area = elements_dict.get("windows", {}).get("area_m2", 0.0)
    if include_doors and "doors" in elements_dict:
        window_area += elements_dict["doors"].get("area_m2", 0.0)

    if external_wall_area > 0:
        return window_area / external_wall_area
    else:
        return 0.0




def get_extended_materials_data(
    building_function: str,
    building_type: str,      # e.g. "Two-and-a-half-story House" or "Meeting Function"
    age_range: str,
    scenario: str,
    calibration_stage: str,
    strategy: str = "A",
    random_seed=None,
    user_config_fenez=None   # optional user override
):
    """
    1) Looks up either residential_materials_data or non_residential_materials_data
       by (building_type, age_range, scenario, calibration_stage).
    2) Picks from wwr_range => final wwr.
    3) Also grabs top-level 'material_opaque_lookup', 'material_window_lookup' if any.
    4) Then for sub-elements => ground_floor, windows, doors => picks R_value, U_value, area, etc.
       plus references to 'material_opaque_lookup' or 'material_window_lookup' if present.
    5) If user_config_fenez is provided, it can override some or all picks at the end.
    6) Finally, we recompute conductivity or thermal_resistance to ensure the final
       R or U from data_materials_xxx is used. 
    7) Returns a dictionary => {
         "roughness": ...,
         "wwr": ...,
         "material_opaque": ...,
         "material_window": ...,
         "elements": {...}
       }
    """

    if random_seed is not None:
        random.seed(random_seed)

    # Decide data source
    if building_function.lower() == "residential":
        ds = residential_materials_data
        dict_key = (building_type, age_range, scenario, calibration_stage)
    else:
        ds = non_residential_materials_data
        dict_key = (building_type, age_range, scenario, calibration_stage)

    # If no matching entry, return a fallback
    if dict_key not in ds:
        output_fallback = {
            "roughness": "MediumRough",
            "wwr": 0.3,
            "material_opaque": None,
            "material_window": None,
            "elements": {}
        }
        # Optionally let user_config_fenez override WWR even in fallback
        if user_config_fenez is not None and "wwr" in user_config_fenez:
            output_fallback["wwr"] = user_config_fenez["wwr"]
        return output_fallback

    data_entry = ds[dict_key]

    # 1) pick wwr
    wwr_val = pick_val(data_entry.get("wwr_range", (0.3, 0.3)), strategy)
    # 2) get roughness
    rough_str = data_entry.get("roughness", "MediumRough")

    # 3) top-level opaque and window lookups
    mat_opq_key = data_entry.get("material_opaque_lookup", None)
    final_opq = None
    if mat_opq_key and mat_opq_key in material_lookup:
        final_opq = assign_material_from_lookup(material_lookup[mat_opq_key], strategy)

    mat_win_key = data_entry.get("material_window_lookup", None)
    final_win = None
    if mat_win_key and mat_win_key in material_lookup:
        final_win = assign_material_from_lookup(material_lookup[mat_win_key], strategy)

    # 4) sub-elements => gather them
    elements = {}
    possible_elements = [
        "ground_floor", "solid_wall", "sloping_flat_roof", "exterior_wall",
        "flat_roof", "windows", "doors"
    ]

    for elem_name in possible_elements:
        if elem_name in data_entry:
            subd = data_entry[elem_name]
            out_sub = dict(subd)  # shallow copy

            # pick R_value
            if "R_value_range" in subd:
                out_sub["R_value"] = pick_val(subd["R_value_range"], strategy)
            # pick U_value
            if "U_value_range" in subd:
                out_sub["U_value"] = pick_val(subd["U_value_range"], strategy)

            # if subd has its own lookups
            if "material_opaque_lookup" in subd:
                mokey = subd["material_opaque_lookup"]
                if mokey in material_lookup:
                    out_sub["material_opaque"] = assign_material_from_lookup(
                        material_lookup[mokey], strategy
                    )
            if "material_window_lookup" in subd:
                mwkey = subd["material_window_lookup"]
                if mwkey in material_lookup:
                    out_sub["material_window"] = assign_material_from_lookup(
                        material_lookup[mwkey], strategy
                    )

            elements[elem_name] = out_sub

    # 5) Build initial result
    result = {
        "roughness": rough_str,
        "wwr": wwr_val,
        "material_opaque": final_opq,
        "material_window": final_win,
        "elements": elements
    }

    # 6) user_config_fenez override
    if user_config_fenez is not None:
        # override top-level WWR
        if "wwr" in user_config_fenez:
            result["wwr"] = user_config_fenez["wwr"]
        # override top-level material_opaque_lookup
        if "material_opaque_lookup" in user_config_fenez:
            new_opq_key = user_config_fenez["material_opaque_lookup"]
            if new_opq_key in material_lookup:
                result["material_opaque"] = assign_material_from_lookup(
                    material_lookup[new_opq_key], strategy
                )
        # override top-level material_window_lookup
        if "material_window_lookup" in user_config_fenez:
            new_win_key = user_config_fenez["material_window_lookup"]
            if new_win_key in material_lookup:
                result["material_window"] = assign_material_from_lookup(
                    material_lookup[new_win_key], strategy
                )
        # override any sub-elements
        if "elements" in user_config_fenez:
            for elem_key, elem_val in user_config_fenez["elements"].items():
                if elem_key not in result["elements"]:
                    result["elements"][elem_key] = {}
                # override R, U, area, lookups, etc.
                if "R_value" in elem_val:
                    result["elements"][elem_key]["R_value"] = elem_val["R_value"]
                if "U_value" in elem_val:
                    result["elements"][elem_key]["U_value"] = elem_val["U_value"]
                if "area_m2" in elem_val:
                    result["elements"][elem_key]["area_m2"] = elem_val["area_m2"]
                if "material_opaque_lookup" in elem_val:
                    mk = elem_val["material_opaque_lookup"]
                    if mk in material_lookup:
                        result["elements"][elem_key]["material_opaque"] = assign_material_from_lookup(
                            material_lookup[mk], strategy
                        )
                if "material_window_lookup" in elem_val:
                    mwk = elem_val["material_window_lookup"]
                    if mwk in material_lookup:
                        result["elements"][elem_key]["material_window"] = assign_material_from_lookup(
                            material_lookup[mwk], strategy
                        )

    # 7) Post-processing to ENFORCE final R_value / U_value from data_materials_xxx
    #    => override Conductivity or Thermal_Resistance so R or U is correct.
    for elem_name, elem_data in result["elements"].items():
        # gather final R or U
        r_val = elem_data.get("R_value", None)
        u_val = elem_data.get("U_value", None)
        if r_val is None and u_val is not None:
            # if only U is known, convert to R
            if u_val != 0:
                r_val = 1.0 / u_val

        # override opaque material if we have an R
        mat_opq = elem_data.get("material_opaque", None)
        if mat_opq and r_val is not None:
            if mat_opq["obj_type"].upper() == "MATERIAL":
                # For a mass-based material => R = thickness / conductivity
                # => conductivity = thickness / R
                thickness = mat_opq["Thickness"]
                if r_val != 0:
                    mat_opq["Conductivity"] = thickness / r_val
            elif mat_opq["obj_type"].upper() == "MATERIAL:NOMASS":
                # For a no-mass => thermal_resistance = R
                mat_opq["Thermal_Resistance"] = r_val

        # override window material if we have a U (approx single glazing)
        mat_win = elem_data.get("material_window", None)
        if mat_win and u_val is not None:
            if mat_win["obj_type"].upper() == "WINDOWMATERIAL:GLAZING":
                # For single-pane glass, approximate:
                #   U ~ (conductivity / thickness) ignoring film coefs,
                #   so conductivity = U * thickness
                thickness = mat_win["Thickness"]
                mat_win["Conductivity"] = u_val * thickness

    return result
