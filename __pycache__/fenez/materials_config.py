# fenez/materials_config.py

import random
from .materials_lookup import material_lookup
from .data_materials_residential import residential_materials_data
from .data_materials_non_residential import non_residential_materials_data


###############################################################################
#                               pick_val
###############################################################################
def pick_val(rng, strategy="A"):
    """
    A simple helper to pick a float from (min_val, max_val) without logging.

    Args:
        rng (tuple): (min_val, max_val).
        strategy (str): "A" => picks midpoint, "B" => random in [min_val,max_val], else => picks min_val.

    Returns:
        float: The chosen numeric value.
    """
    if rng[0] == rng[1]:
        return rng[0]
    if strategy == "A":
        return 0.5 * (rng[0] + rng[1])
    elif strategy == "B":
        return random.uniform(rng[0], rng[1])
    else:
        return rng[0]


###############################################################################
#                           pick_val_with_range
###############################################################################
def pick_val_with_range(rng_tuple, strategy="A", log_dict=None, param_name=None):
    """
    Picks a float from (min_val, max_val) and optionally logs both the chosen value
    and the range into a dictionary.

    Args:
        rng_tuple (tuple): (min_val, max_val).
        strategy (str): "A" => midpoint, "B" => random uniform, else => min_val fallback.
        log_dict (dict): If provided, we store both param_name -> chosen_value
                         and param_name+"_range" -> (min_val, max_val).
        param_name (str): e.g. "fenez_wwr", "fenez_exterior_wall_R_value".

    Returns:
        float: The chosen numeric value.
    """
    if rng_tuple[0] == rng_tuple[1]:
        chosen = rng_tuple[0]
    else:
        if strategy == "A":
            chosen = 0.5 * (rng_tuple[0] + rng_tuple[1])
        elif strategy == "B":
            chosen = random.uniform(rng_tuple[0], rng_tuple[1])
        else:
            chosen = rng_tuple[0]

    if log_dict is not None and param_name is not None:
        # Example => log_dict["fenez_wwr"] = 0.28
        #            log_dict["fenez_wwr_range"] = (0.2, 0.35)
        log_dict[param_name] = chosen
        log_dict[f"{param_name}_range"] = rng_tuple

    return chosen


###############################################################################
#                    assign_material_from_lookup
###############################################################################
def assign_material_from_lookup(mat_def: dict, strategy="A", log_dict=None, param_prefix=""):
    """
    Takes a material definition (from materials_lookup) with fields like "Thickness_range",
    "Conductivity_range", etc. Then picks final numeric fields, optionally logging them.

    Args:
        mat_def (dict): e.g. material_lookup["Concrete_200mm"] => {
                            "obj_type": "MATERIAL",
                            "Thickness_range": (0.195, 0.205),
                            ...
                         }
        strategy (str): "A" => pick midpoint, "B" => random, else => min_val fallback.
        log_dict (dict): e.g. assigned_fenez_log[bldg_id], so we can store picks:
                         log_dict[f"{param_prefix}.Thickness"], etc.
        param_prefix (str): prefix used in logging, e.g. "fenez_top_opq".

    Returns:
        dict: A copy of the original mat_def with final numeric picks assigned for each field.
    """
    final_mat = dict(mat_def)  # shallow copy
    obj_type = final_mat["obj_type"].upper()

    # A nested helper to pick a single field from the range and log it.
    def store_and_pick(field_name):
        rng = final_mat.get(f"{field_name}_range")
        if rng is not None:
            full_param_name = f"{param_prefix}.{field_name}" if param_prefix else field_name
            chosen_val = pick_val_with_range(rng, strategy, log_dict, full_param_name)
            final_mat[field_name] = chosen_val

    if obj_type == "MATERIAL":
        store_and_pick("Thickness")
        store_and_pick("Conductivity")
        store_and_pick("Density")
        store_and_pick("Specific_Heat")
        store_and_pick("Thermal_Absorptance")
        store_and_pick("Solar_Absorptance")
        store_and_pick("Visible_Absorptance")

    elif obj_type == "MATERIAL:NOMASS":
        store_and_pick("Thermal_Resistance")
        store_and_pick("Thermal_Absorptance")
        store_and_pick("Solar_Absorptance")
        store_and_pick("Visible_Absorptance")

    elif obj_type == "WINDOWMATERIAL:GLAZING":
        store_and_pick("Thickness")
        store_and_pick("Solar_Transmittance")
        store_and_pick("Front_Solar_Reflectance")
        store_and_pick("Back_Solar_Reflectance")
        store_and_pick("Visible_Transmittance")
        store_and_pick("Front_Visible_Reflectance")
        store_and_pick("Back_Visible_Reflectance")
        store_and_pick("Front_IR_Emissivity")
        store_and_pick("Back_IR_Emissivity")
        store_and_pick("Conductivity")
        store_and_pick("Dirt_Correction_Factor")
        # If IR_Transmittance or Solar_Diffusing is fixed or no range, you can leave it as-is.

    # elif obj_type == "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM":
    #     store_and_pick("UFactor")
    #     store_and_pick("SHGC")
    #     ...

    return final_mat


###############################################################################
#                              compute_wwr
###############################################################################
def compute_wwr(elements_dict, include_doors=False):
    """
    Computes Window-to-Wall Ratio (WWR) = (window area) / (external wall area).

    Args:
        elements_dict (dict): e.g. the "elements" dictionary from get_extended_materials_data(...).
        include_doors (bool): If True, door area is added to the numerator.

    Returns:
        float: The final WWR ratio (0 <= x <= 1+?), or 0.0 if there's no external wall area.
    """
    external_wall_area = 0.0
    if "solid_wall" in elements_dict:
        external_wall_area += elements_dict["solid_wall"].get("area_m2", 0.0)
    if "exterior_wall" in elements_dict:
        external_wall_area += elements_dict["exterior_wall"].get("area_m2", 0.0)
    # If "sloping_flat_roof" or other keys exist, you can treat them as external surfaces, etc.

    window_area = elements_dict.get("windows", {}).get("area_m2", 0.0)
    if include_doors and "doors" in elements_dict:
        window_area += elements_dict["doors"].get("area_m2", 0.0)

    if external_wall_area > 0:
        return window_area / external_wall_area
    else:
        return 0.0


###############################################################################
#                      get_extended_materials_data
###############################################################################
def get_extended_materials_data(
    building_function: str,
    building_type: str,
    age_range: str,
    scenario: str,
    calibration_stage: str,
    strategy: str = "A",
    random_seed=None,
    user_config_fenez=None,
    assigned_fenez_log=None
):
    """
    Orchestrates the retrieval of building envelope data for a given building,
    picking final numeric values for WWR, R/U-values, material properties, etc.

    Steps:
      1) Pick the correct dictionary (residential or non_residential).
      2) Extract the entry by (building_type, age_range, scenario, calibration_stage).
      3) From that entry:
         - "wwr_range" => pick final "wwr"
         - "material_opaque_lookup", "material_window_lookup" => pick from material_lookup
         - "ground_floor", "windows", "doors", etc. => area, R_value, U_value, sub-lookup, ...
      4) If user_config_fenez is provided, allow overrides of wwr, materials, etc.
      5) Return final dict => {
           "roughness": str,
           "wwr": float,
           "material_opaque": dict of final picks,
           "material_window": dict of final picks,
           "elements": {...}  # sub-element picks
         }

    Args:
        building_function (str): "residential" or "non_residential".
        building_type (str): e.g. "Two-and-a-half-story House", "Meeting Function", ...
        age_range (str): e.g. "<1965", "2015 and later", ...
        scenario (str): e.g. "scenario1".
        calibration_stage (str): e.g. "pre_calibration", "post_calibration".
        strategy (str): "A" => midpoint, "B" => random, etc.
        random_seed (int): For reproducibility, if you want stable random picks.
        user_config_fenez (dict): Optional overrides, e.g. {"wwr": 0.25, ...}.
        assigned_fenez_log (dict): If provided, we store picks here, keyed by building_id.

    Returns:
        dict: e.g. {
          "roughness": "MediumRough",
          "wwr": 0.32,
          "material_opaque": {...},
          "material_window": {...},
          "elements": {
             "ground_floor": {... R_value=..., ...},
             "windows": {... U_value=..., area_m2=..., ...},
             ...
          }
        }
    """
    # Optional random seed
    if random_seed is not None:
        random.seed(random_seed)

    # Decide which data dictionary to use
    if building_function.lower() == "residential":
        ds = residential_materials_data
        dict_key = (building_type, age_range, scenario, calibration_stage)
    else:
        ds = non_residential_materials_data
        dict_key = (building_type, age_range, scenario, calibration_stage)

    # If no matching key => fallback
    if dict_key not in ds:
        fallback = {
            "roughness": "MediumRough",
            "wwr": 0.3,
            "material_opaque": None,
            "material_window": None,
            "elements": {}
        }
        # If user_config_fenez sets a custom wwr, override fallback
        if user_config_fenez and "wwr" in user_config_fenez:
            fallback["wwr"] = user_config_fenez["wwr"]
        return fallback

    data_entry = ds[dict_key]

    # We'll store picks if assigned_fenez_log + building_id is known
    building_id = None
    if assigned_fenez_log and user_config_fenez and "ogc_fid" in user_config_fenez:
        building_id = user_config_fenez["ogc_fid"]

    # 1) pick wwr from "wwr_range"
    wwr_rng = data_entry.get("wwr_range", (0.3, 0.3))
    wwr_val = pick_val_with_range(
        wwr_rng,
        strategy=strategy,
        log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
        param_name="fenez_wwr"
    )

    # 2) get "roughness"
    rough_str = data_entry.get("roughness", "MediumRough")

    # 3) top-level material references
    mat_opq_key = data_entry.get("material_opaque_lookup")
    final_opq = None
    if mat_opq_key and mat_opq_key in material_lookup:
        prefix = "fenez_top_opq"
        final_opq = assign_material_from_lookup(
            material_lookup[mat_opq_key],
            strategy,
            log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
            param_prefix=prefix
        )

    mat_win_key = data_entry.get("material_window_lookup")
    final_win = None
    if mat_win_key and mat_win_key in material_lookup:
        prefix = "fenez_top_win"
        final_win = assign_material_from_lookup(
            material_lookup[mat_win_key],
            strategy,
            log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
            param_prefix=prefix
        )

    # 4) sub-elements
    possible_elems = ["ground_floor", "solid_wall", "sloping_flat_roof",
                      "exterior_wall", "flat_roof", "windows", "doors"]
    elements = {}
    for elem_name in possible_elems:
        if elem_name in data_entry:
            subd = data_entry[elem_name]
            out_sub = dict(subd)  # shallow copy

            # R_value
            rv_rng = subd.get("R_value_range")
            if rv_rng:
                rv_param = f"fenez_{elem_name}_R_value"
                out_sub["R_value"] = pick_val_with_range(
                    rv_rng,
                    strategy,
                    log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
                    param_name=rv_param
                )

            # U_value
            uv_rng = subd.get("U_value_range")
            if uv_rng:
                uv_param = f"fenez_{elem_name}_U_value"
                out_sub["U_value"] = pick_val_with_range(
                    uv_rng,
                    strategy,
                    log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
                    param_name=uv_param
                )

            # sub-element material_opaque_lookup
            if "material_opaque_lookup" in subd:
                opq_lu = subd["material_opaque_lookup"]
                if opq_lu in material_lookup:
                    prefix = f"fenez_{elem_name}_opq"
                    out_sub["material_opaque"] = assign_material_from_lookup(
                        material_lookup[opq_lu],
                        strategy,
                        log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
                        param_prefix=prefix
                    )

            # sub-element material_window_lookup
            if "material_window_lookup" in subd:
                win_lu = subd["material_window_lookup"]
                if win_lu in material_lookup:
                    prefix = f"fenez_{elem_name}_win"
                    out_sub["material_window"] = assign_material_from_lookup(
                        material_lookup[win_lu],
                        strategy,
                        log_dict=assigned_fenez_log.get(building_id) if (assigned_fenez_log and building_id) else None,
                        param_prefix=prefix
                    )

            elements[elem_name] = out_sub

    # Gather final result
    result = {
        "roughness": rough_str,
        "wwr": wwr_val,
        "material_opaque": final_opq,
        "material_window": final_win,
        "elements": elements
    }

    # 5) user_config_fenez overrides
    if user_config_fenez:
        # If user explicitly sets "wwr"
        if "wwr" in user_config_fenez:
            forced_wwr = user_config_fenez["wwr"]
            result["wwr"] = forced_wwr
            if assigned_fenez_log and building_id:
                assigned_fenez_log[building_id]["fenez_wwr"] = forced_wwr
                assigned_fenez_log[building_id]["fenez_wwr_range"] = (forced_wwr, forced_wwr)

        # likewise for other overrides (material_opaque_lookup, etc.)
        # ...
        # e.g. if "material_opaque_lookup" in user_config_fenez: etc.

    return result
