# HVAC/assign_hvac_values.py
import random
from .hvac_lookup import hvac_lookup


def find_hvac_overrides(
    building_id,
    building_function,
    residential_type,
    non_residential_type,
    age_range,
    scenario,
    calibration_stage,
    user_config
):
    """
    Optionally check all these fields.
    If 'residential_type' in row => must match.
    If 'non_residential_type' in row => must match, etc.
    """
    matches = []
    for row in user_config or []:
        if "building_id" in row and row["building_id"] != building_id:
            continue
        if "building_function" in row and row["building_function"] != building_function:
            continue

        # If row has 'residential_type' => must match exactly, etc.
        #   you can skip or adapt if you only want partial checks
        if "residential_type" in row and row["residential_type"] != residential_type:
            continue
        if "non_residential_type" in row and row["non_residential_type"] != non_residential_type:
            continue

        if "age_range" in row and row["age_range"] != age_range:
            continue
        if "scenario" in row and row["scenario"] != scenario:
            continue
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
    rng_tuple = (min_val, max_val).
    strategy  = "A" => midpoint, "B" => random, else => pick min_val.
    log_dict  => assigned_hvac_log[bldg_id].
    param_name=> e.g. "heating_day_setpoint".

    We'll store log_dict[f"{param_name}_range"] = rng_tuple
               log_dict[param_name]            = chosen
    """
    min_v, max_v = rng_tuple

    if strategy == "A":  # midpoint
        chosen = (min_v + max_v) / 2.0
    elif strategy == "B":
        chosen = random.uniform(min_v, max_v)
    else:
        chosen = min_v

    if log_dict is not None and param_name:
        log_dict[f"{param_name}_range"] = (min_v, max_v)
        log_dict[param_name] = chosen

    return chosen


def assign_hvac_ideal_parameters(
    building_id=None,
    building_function=None,
    residential_type=None,
    non_residential_type=None,
    age_range=None,
    scenario=None,
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config_hvac=None,
    assigned_hvac_log=None
):
    """
    1) We interpret hvac_lookup[calibration_stage][scenario][building_function]
       then either [residential_type] or [non_residential_type], then [age_range].
    2) That sub-dict provides the *range* for
        - heating_day_setpoint_range
        - heating_night_setpoint_range
        - cooling_day_setpoint_range
        - cooling_night_setpoint_range
        - max_heating_supply_air_temp_range
        - min_cooling_supply_air_temp_range
      plus possibly "schedule_details".
    3) Apply user_config overrides => update those ranges.
    4) pick final values with pick_val_with_range => store in assigned_hvac_log
    5) return final hvac_params
    """

    # For reproducibility
    if random_seed is not None:
        random.seed(random_seed)

    # Fallback if stage not in hvac_lookup
    if calibration_stage not in hvac_lookup:
        calibration_stage = "pre_calibration"

    # Now we must index deeper, e.g. hvac_lookup[calibration_stage][scenario][building_function][res_type][age_range]
    stage_block = hvac_lookup[calibration_stage]

    if scenario not in stage_block:
        scenario = next(iter(stage_block.keys()))  # fallback to first scenario
    scenario_block = stage_block[scenario]

    if building_function not in scenario_block:
        building_function = next(iter(scenario_block.keys()))  # fallback
    bf_block = scenario_block[building_function]

    # pick sub_type
    # If building_function=="residential", we use 'residential_type'
    # If building_function=="non_residential", we use 'non_residential_type'
    if building_function.lower() == "residential":
        subtype = residential_type or next(iter(bf_block.keys()))
    else:
        subtype = non_residential_type or next(iter(bf_block.keys()))

    # Now get sub_block = bf_block[subtype], then sub_block[age_range]
    if subtype not in bf_block:
        # fallback => pick first
        subtype = next(iter(bf_block.keys()))
    sub_block = bf_block[subtype]

    if age_range not in sub_block:
        # fallback => pick first age_range
        age_range = next(iter(sub_block.keys()))
    final_block = sub_block[age_range]

    # final_block should have e.g.:
    # {
    #   "heating_day_setpoint_range": (19,21),
    #   "heating_night_setpoint_range": (15,16),
    #   ...
    #   "schedule_details": {...}
    # }

    # Extract the base ranges
    heat_day_rng    = final_block.get("heating_day_setpoint_range", (20.0, 20.0))
    heat_night_rng  = final_block.get("heating_night_setpoint_range", (16.0, 16.0))
    cool_day_rng    = final_block.get("cooling_day_setpoint_range", (25.0, 25.0))
    cool_night_rng  = final_block.get("cooling_night_setpoint_range", (27.0, 27.0))
    max_heat_air_rng= final_block.get("max_heating_supply_air_temp_range", (50.0, 50.0))
    min_cool_air_rng= final_block.get("min_cooling_supply_air_temp_range", (13.0, 13.0))

    # If there's schedule_details => we can store or parse it as well
    schedule_details = final_block.get("schedule_details", {})

    # Now apply user_config overrides if any
    matches = []
    if user_config_hvac:
        matches = find_hvac_overrides(
            building_id or 0,
            building_function or "",
            residential_type or "",
            non_residential_type or "",
            age_range or "",
            scenario or "",
            calibration_stage,
            user_config_hvac
        )

    def override_range(current_range, row):
        if "fixed_value" in row:
            v = row["fixed_value"]
            return (v, v)
        if "min_val" in row and "max_val" in row:
            return (row["min_val"], row["max_val"])
        return current_range

    for row in matches:
        pname = row.get("param_name")
        if pname == "heating_day_setpoint":
            heat_day_rng = override_range(heat_day_rng, row)
        elif pname == "heating_night_setpoint":
            heat_night_rng = override_range(heat_night_rng, row)
        elif pname == "cooling_day_setpoint":
            cool_day_rng = override_range(cool_day_rng, row)
        elif pname == "cooling_night_setpoint":
            cool_night_rng = override_range(cool_night_rng, row)
        elif pname == "max_heating_supply_air_temp":
            max_heat_air_rng = override_range(max_heat_air_rng, row)
        elif pname == "min_cooling_supply_air_temp":
            min_cool_air_rng = override_range(min_cool_air_rng, row)
        # optionally schedule_details overrides if row has schedule_key etc.

    # ensure assigned_hvac_log subdict
    if assigned_hvac_log is not None and building_id not in assigned_hvac_log:
        assigned_hvac_log[building_id] = {}

    log_dict = assigned_hvac_log[building_id] if assigned_hvac_log and building_id else None


    schedule_details = final_block.get("schedule_details", {})




    # pick final
    hvac_params = {}
    hvac_params["heating_day_setpoint"] = pick_val_with_range(heat_day_rng, strategy, log_dict, "heating_day_setpoint")
    hvac_params["heating_night_setpoint"] = pick_val_with_range(heat_night_rng, strategy, log_dict, "heating_night_setpoint")
    hvac_params["cooling_day_setpoint"] = pick_val_with_range(cool_day_rng, strategy, log_dict, "cooling_day_setpoint")
    hvac_params["cooling_night_setpoint"] = pick_val_with_range(cool_night_rng, strategy, log_dict, "cooling_night_setpoint")
    hvac_params["max_heating_supply_air_temp"] = pick_val_with_range(max_heat_air_rng, strategy, log_dict, "max_heating_supply_air_temp")
    hvac_params["min_cooling_supply_air_temp"] = pick_val_with_range(min_cool_air_rng, strategy, log_dict, "min_cooling_supply_air_temp")

    # if you want to store schedule_details in the log too
    if log_dict is not None:
        log_dict["schedule_details"] = schedule_details




        # then handle schedule_details separately:
    if schedule_details:
        # We'll store them as separate param_name => param_val lines in the hvac log.
        # e.g. "schedule_day_start", "schedule_day_end", "schedule_weekend_day_start", etc.
        for k, v in schedule_details.items():
            # example: k="day_start", v="07:00"
            # we'll create param_name = f"schedule_{k}"
            param_name = f"schedule_{k}"
            if log_dict is not None:
                log_dict[param_name] = v
                # no numeric range => so we do NOT do param_name_range
                # because schedule strings do not have min/max


    return hvac_params
