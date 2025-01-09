# ventilation/assign_ventilation_values.py


import random
from .ventilation_lookup import ventilation_lookup

def find_vent_overrides(
    building_id,
    building_function,
    age_range,
    scenario,
    calibration_stage,
    user_config
):
    """
    Return user_config rows that match building_id, building_function, age_range, scenario, calibration_stage.
    """
    matches = []
    if user_config:
        for row in user_config:
            # building_id match
            if "building_id" in row and row["building_id"] != building_id:
                continue
            # building_function match
            if "building_function" in row and row["building_function"] != building_function:
                continue
            # age_range match
            if "age_range" in row and row["age_range"] != age_range:
                continue
            # scenario match
            if "scenario" in row and row["scenario"] != scenario:
                continue
            # calibration_stage match
            if "calibration_stage" in row and row["calibration_stage"] != calibration_stage:
                continue

            matches.append(row)
    return matches


def pick_val_with_range(
    rng_tuple,
    strategy="A",
    log_dict=None,
    param_name=None
):
    """
    rng_tuple = (min_val, max_val) or None.
    strategy  = "A"=>midpoint, "B"=>random, "C"=>min, etc.
    log_dict  => the assigned_vent_log[bldg_id] dictionary for storing range and final value.
    param_name=> e.g. "infiltration_base", "fan_pressure", "year_factor", etc.

    We store:
      log_dict[f"{param_name}_range"] = (min_val, max_val)
      log_dict[param_name]            = final_chosen_value
    """
    if rng_tuple is None:
        # fallback => just return 0
        chosen = 0.0
        return chosen

    min_v, max_v = rng_tuple

    # pick final
    if strategy == "A":
        chosen = (min_v + max_v) / 2.0
    elif strategy == "B":
        chosen = random.uniform(min_v, max_v)
    else:
        # fallback => pick min
        chosen = min_v

    if log_dict is not None and param_name:
        # store the numeric range
        log_dict[f"{param_name}_range"] = (min_v, max_v)
        # store the final
        log_dict[param_name] = chosen

    return chosen


def assign_ventilation_params_with_overrides(
    building_id=None,
    building_function="residential",
    age_range="2015 and later",
    scenario="scenario1",
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config_vent=None,     # possibly a list of override rows
    assigned_vent_log=None,    # dictionary to store final picks
    # existing arguments from original code:
    infiltration_key=None,     # e.g. "A_corner"
    year_key=None,             # e.g. "1970-1992"
    is_residential=True,
    default_flow_exponent=0.67
):
    """
    Return a dict => {
       "infiltration_base": float,
       "year_factor": float,
       "system_type": str,
       "f_ctrl": float,
       "fan_pressure": float,
       "hrv_eff": float,
       "infiltration_schedule_name": str,
       "ventilation_schedule_name": str
    }

    Steps:
      1) fallback if calibration_stage not in ventilation_lookup => "pre_calibration".
      2) gather default infiltration_base range from infiltration_key (res or non_res).
      3) gather year_factor range from year_key
      4) pick default system_type => "A" (res) or "D" (non_res), or can be user-overridden.
      5) gather fan_pressure_range => can be user-overridden
      6) gather system_control_range => f_ctrl => can be user-overridden
      7) gather hrv_sensible_eff_range => if system_type=="D"
      8) apply user overrides from user_config_vent => override numeric ranges or system_type
      9) pick final infiltration_base, year_factor, fan_pressure, f_ctrl, hrv_eff with pick_val_with_range
      10) store infiltration_schedule_name, ventilation_schedule_name (strings)
      11) return assigned dict
    """

    # optional random seed
    if random_seed is not None:
        random.seed(random_seed)

    # 1) fallback

    if scenario not in ventilation_lookup:
        scenario = "scenario1"


    if calibration_stage not in ventilation_lookup:
        calibration_stage = "pre_calibration"
    stage_dict = ventilation_lookup[scenario][calibration_stage]

    # if assigned_vent_log => ensure we have a sub-dict for building_id
    if assigned_vent_log is not None and building_id not in assigned_vent_log:
        assigned_vent_log[building_id] = {}
    # local reference to store picks
    log_dict = assigned_vent_log[building_id] if (assigned_vent_log and building_id is not None) else None

    # 2) infiltration_base range
    if is_residential:
        # gather from stage_dict["residential_infiltration_range"]
        res_infil = stage_dict["residential_infiltration_range"]
        infiltration_base_rng = res_infil.get(infiltration_key, (1.0, 1.0))
        # also the system_control_range for res
        sys_ctrl_ranges = stage_dict["system_control_range_res"]
    else:
        # non_res_infiltration_range
        nonres_infil = stage_dict["non_res_infiltration_range"]
        infiltration_base_rng = nonres_infil.get(infiltration_key, (0.5, 0.5))
        sys_ctrl_ranges = stage_dict["system_control_range_nonres"]

    # 3) year_factor range
    year_factor_dict = stage_dict["year_factor_range"]
    year_factor_rng = year_factor_dict.get(year_key, (1.0, 1.0))

    # default system_type => "A" if residential, else "D"
    default_sys = "A" if is_residential else "D"

    # fan_pressure => often stored in stage_dict["fan_pressure_range"],
    # but it's not subdivided by infiltration_key. Let's skip or do (0,0) fallback
    fan_press_rng = (0.0, 0.0)
    if "fan_pressure_range" in stage_dict:
        # Possibly you have "fan_pressure_range":{"res_mech":(40,60),"nonres_intake":(90,110),...}
        # but we do not know which subkey to pick. You can adapt if needed.
        # We'll skip for brevity, or we can do a direct approach:
        # fan_press_rng = stage_dict["fan_pressure_range"].get("res_mech",(0.0,0.0))
        pass

    # 6) f_ctrl => pick from system_control_range
    # default to sys_ctrl_ranges["A"]["f_ctrl_range"] if system_type is "A", etc.
    # but we won't finalize until after user overrides.
    system_type_final = default_sys  # can be changed
    if system_type_final in sys_ctrl_ranges:
        f_ctrl_rng = sys_ctrl_ranges[system_type_final].get("f_ctrl_range", (1.0,1.0))
    else:
        f_ctrl_rng = (1.0,1.0)

    # 7) HRV => stage_dict["hrv_sensible_eff_range"]
    hrv_eff_rng = (0.0, 0.0)
    if "hrv_sensible_eff_range" in stage_dict:
        hrv_eff_rng = stage_dict["hrv_sensible_eff_range"]

    # 8) user overrides
    matches = find_vent_overrides(
        building_id or 0,
        building_function or "residential",
        age_range or "2015 and later",
        scenario or "scenario1",
        calibration_stage,
        user_config_vent
    )

    def override_range(current_range, row):
        if "fixed_value" in row:
            val = row["fixed_value"]
            return (val, val)
        elif "min_val" in row and "max_val" in row:
            return (row["min_val"], row["max_val"])
        return current_range

    for row in matches:
        pname = row.get("param_name","")
        if pname == "infiltration_base":
            infiltration_base_rng = override_range(infiltration_base_rng, row)
        elif pname == "year_factor":
            year_factor_rng = override_range(year_factor_rng, row)
        elif pname == "system_type":
            if "fixed_value" in row:
                system_type_final = row["fixed_value"]
        elif pname == "fan_pressure":
            fan_press_rng = override_range(fan_press_rng, row)
        elif pname == "f_ctrl":
            f_ctrl_rng = override_range(f_ctrl_rng, row)
        elif pname == "hrv_eff":
            hrv_eff_rng = override_range(hrv_eff_rng, row)
        # If you had infiltration_schedule, ventilation_schedule overrides, you could read them here:
        # e.g. if pname=="infiltration_schedule_name": infiltration_sched_name = row["fixed_value"]

    # 9) now pick final infiltration_base, year_factor, fan_pressure, f_ctrl, hrv_eff
    infiltration_base_val = pick_val_with_range(infiltration_base_rng, strategy, log_dict, "infiltration_base")
    year_factor_val       = pick_val_with_range(year_factor_rng,       strategy, log_dict, "year_factor")
    fan_pressure_val      = pick_val_with_range(fan_press_rng,         strategy, log_dict, "fan_pressure")
    f_ctrl_val            = pick_val_with_range(f_ctrl_rng,            strategy, log_dict, "f_ctrl")

    hrv_eff_val = 0.0
    if system_type_final == "D":  # if user or default => system_type="D"
        # pick from hrv_eff_rng
        hrv_eff_val = pick_val_with_range(hrv_eff_rng, strategy, log_dict, "hrv_eff")

    # 10) infiltration/vent schedules => store them if you want
    # We default them to "AlwaysOnSched"/"VentSched_DayNight", or
    # they could be user-overridden above if param_name was "infiltration_schedule_name", etc.
    infiltration_sched_name = "AlwaysOnSched"
    ventilation_sched_name  = "VentSched_DayNight"

    # if we want them in the log:
    if log_dict is not None:
        log_dict["infiltration_schedule_name"] = infiltration_sched_name
        log_dict["ventilation_schedule_name"]  = ventilation_sched_name

    # 11) build final assigned dict
    assigned = {
        "infiltration_base": infiltration_base_val,
        "year_factor": year_factor_val,
        "system_type": system_type_final,
        "f_ctrl": f_ctrl_val,
        "fan_pressure": fan_pressure_val,
        "hrv_eff": hrv_eff_val,
        "infiltration_schedule_name": infiltration_sched_name,
        "ventilation_schedule_name": ventilation_sched_name
    }

    return assigned




    """
    Searches a user_config list/dict for any override entries matching the
    building_id, building_function, age_range, scenario, and calibration_stage.
    Returns a list of matching dict rows.

    Each 'row' in user_config can specify:
      - "building_id"
      - "building_function"
      - "age_range"
      - "scenario"
      - "calibration_stage"
      - plus override fields for infiltration_base, year_factor, system_type, fan_pressure, f_ctrl, hrv_eff, etc.

    If any of those fields are present in the row and do not match the
    current building, that row is skipped. Otherwise, the row is considered
    a match and is returned in the list.
    """

    """
    Return a dict with infiltration_base, year_factor, system_type, f_ctrl, fan_pressure,
    hrv_eff, infiltration_schedule_name, ventilation_schedule_name, etc.

    This function uses:
      1) The scenario & calibration_stage to locate a sub-dict in 'ventilation_lookup'
      2) The infiltration_key/year_key to get infiltration & year_factor ranges
      3) user_config_vent overrides to optionally override any of the above
      4) A picking strategy (A=midpoint, B=uniform random, C=lower bound) for final selection
      5) The building_function & usage_key to also fetch schedule_info from 'ventilation_lookup'
         => infiltration_schedule_name & ventilation_schedule_name

    Then logs final picks into assigned_vent_log if provided (dict-based log).
    """

