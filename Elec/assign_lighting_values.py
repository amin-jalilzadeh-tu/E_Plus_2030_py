# Elec/assign_lighting_values.py

import random
from .lighting_lookup import lighting_lookup
from .constants import (
    DEFAULT_LIGHTING_WM2,
    DEFAULT_PARASITIC_WM2,
    DEFAULT_TD,
    DEFAULT_TN
)
from .overrides_helper import find_applicable_overrides  # or define inline

def assign_lighting_parameters(
    building_id: int,
    building_type: str,
    age_range=None,
    calibration_stage: str = "pre_calibration",
    strategy: str = "A",
    random_seed: int = None,
    user_config: list = None,     # override table
    assigned_log: dict = None     # optional dictionary to store final picks
):
    """
    Returns a dict with "lights_wm2", "parasitic_wm2", "tD", "tN".
    
    Steps:
      1) Grab default ranges from lighting_lookup[calibration_stage][building_type].
      2) Find all matching override rows for (building_id, building_type).
      3) If any row => override param_name's (min_val, max_val).
      4) Pick final value from the resulting range using strategy (A=midpoint, B=random).
      5) Optionally log the final assignment into assigned_log[building_id].
    """

    if random_seed is not None:
        random.seed(random_seed)

    # 1) Check calibration_stage
    if calibration_stage not in lighting_lookup:
        calibration_stage = "pre_calibration"
    stage_dict = lighting_lookup[calibration_stage]

    # 2) Fallback if building_type not found
    if building_type not in stage_dict:
        # Return defaults
        res = {
            "lights_wm2": DEFAULT_LIGHTING_WM2,
            "parasitic_wm2": DEFAULT_PARASITIC_WM2,
            "tD": DEFAULT_TD,
            "tN": DEFAULT_TN
        }
        if assigned_log is not None:
            assigned_log[building_id] = res
        return res

    param_dict = stage_dict[building_type]

    # Extract default ranges
    lights_rng    = param_dict.get("LIGHTS_WM2_range", (DEFAULT_LIGHTING_WM2, DEFAULT_LIGHTING_WM2))
    parasitic_rng = param_dict.get("PARASITIC_WM2_range", (DEFAULT_PARASITIC_WM2, DEFAULT_PARASITIC_WM2))
    tD_rng        = param_dict.get("tD_range", (DEFAULT_TD, DEFAULT_TD))
    tN_rng        = param_dict.get("tN_range", (DEFAULT_TN, DEFAULT_TN))

    # 3) Find override rows
    if user_config is not None:
        matches = find_applicable_overrides(building_id, building_type, age_range, user_config)

    else:
        matches = []

    # 4) For each match, apply override for the param
    for row in matches:
        pname = row["param_name"]
        mn = row["min_val"]
        mx = row["max_val"]
        if pname == "lights_wm2":
            lights_rng = (mn, mx)
        elif pname == "parasitic_wm2":
            parasitic_rng = (mn, mx)
        elif pname == "tD":
            tD_rng = (mn, mx)
        elif pname == "tN":
            tN_rng = (mn, mx)
        # else ignore

    def pick_val(r):
        if strategy == "A":  # midpoint
            return (r[0] + r[1]) / 2.0
        elif strategy == "B":  # random
            return random.uniform(r[0], r[1])
        else:
            return r[0]

    assigned = {
        "lights_wm2": pick_val(lights_rng),
        "parasitic_wm2": pick_val(parasitic_rng),
        "tD": pick_val(tD_rng),
        "tN": pick_val(tN_rng)
    }

    # 5) Log if needed
    if assigned_log is not None:
        assigned_log[building_id] = assigned

    return assigned
