# ventilation/add_ventilation.py

from ventilation.assign_ventilation_values import assign_ventilation_params_with_overrides
from ventilation.schedules import (
    create_always_on_schedule,
    create_day_night_schedule,
    create_workhours_schedule
)
from ventilation.create_ventilation_systems import create_ventilation_system
from ventilation.calc_functions import calc_infiltration, calc_required_ventilation_flow
from ventilation.mappings import (
    safe_lower,
    map_age_range_to_year_key,
    map_infiltration_key,
    map_usage_key
)

def add_ventilation_to_idf(
    idf,
    building_row,
    calibration_stage="pre_calibration",
    strategy="A",            # "A" => pick midpoint, "B" => random, "C" => pick min, etc.
    random_seed=None,
    user_config_vent=None,
    assigned_vent_log=None
):
    """
    Adds infiltration + ventilation to the IDF based on building_row data,
    referencing infiltration base/year_factor/system_type from our override-based function.
    Then, if system_type == "D", sets hrv_eff on the existing IdealLoads objects.
    """

    # 1) Ensure key schedules exist (the default ones)
    if not idf.getobject("SCHEDULE:CONSTANT", "AlwaysOnSched"):
        create_always_on_schedule(idf, "AlwaysOnSched")
    if not idf.getobject("SCHEDULE:COMPACT", "VentSched_DayNight"):
        create_day_night_schedule(idf, "VentSched_DayNight")
    if not idf.getobject("SCHEDULE:COMPACT", "WorkHoursSched"):
        create_workhours_schedule(idf, "WorkHoursSched")

    # 2) Extract building data
    bldg_id = building_row.get("ogc_fid", 0)
    bldg_func = safe_lower(building_row.get("building_function", "residential"))
    if bldg_func not in ("residential", "non_residential"):
        bldg_func = "residential"

    age_range_str = building_row.get("age_range", "2015 and later")
    year_key = map_age_range_to_year_key(age_range_str)

    infiltration_key = map_infiltration_key(building_row)
    usage_key = map_usage_key(building_row)

    is_res = (bldg_func == "residential")
    floor_area_m2 = building_row.get("area", 100.0)
    scenario = building_row.get("scenario", "scenario1")

    # 3) Assign infiltration & ventilation parameters (including schedules) via override function
    assigned_vent = assign_ventilation_params_with_overrides(
        building_id=bldg_id,
        building_function=bldg_func,
        age_range=age_range_str,
        scenario=scenario,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_vent=user_config_vent,
        assigned_vent_log=assigned_vent_log,
        infiltration_key=infiltration_key,
        year_key=year_key,
        is_residential=is_res,
        default_flow_exponent=0.67
    )

    # Extract the assigned infiltration/vent params
    infiltration_base = assigned_vent["infiltration_base"]
    year_factor       = assigned_vent["year_factor"]
    system_type       = assigned_vent["system_type"]
    f_ctrl_val        = assigned_vent["f_ctrl"]
    fan_pressure      = assigned_vent["fan_pressure"]
    hrv_eff           = assigned_vent["hrv_eff"]

    # (NEW) Extract infiltration/ventilation schedule names (fallback if missing)
    infiltration_sched = assigned_vent.get("infiltration_schedule_name", "AlwaysOnSched")
    ventilation_sched  = assigned_vent.get("ventilation_schedule_name",  "VentSched_DayNight")

    print(
        f"[VENT OVERRIDES] For bldg_id={bldg_id}, infiltration={infiltration_base}, "
        f"year_factor={year_factor}, sys={system_type}, fanP={fan_pressure}, hrv_eff={hrv_eff}"
    )

    # 4) Calculate total infiltration flow (m³/s)
    infiltration_m3_s_total = calc_infiltration(
        infiltration_base=infiltration_base,
        year_factor=year_factor,
        flow_exponent=0.67,
        floor_area_m2=floor_area_m2
    )

    # 5) Calculate total ventilation flow (m³/s)
    vent_flow_m3_s_total = calc_required_ventilation_flow(
        building_function=bldg_func,
        f_ctrl_val=f_ctrl_val,
        floor_area_m2=floor_area_m2,
        usage_key=usage_key
    )

    # 6) Distribute flows to zones
    zones = idf.idfobjects["ZONE"]
    if not zones:
        print("[VENT] No zones found, skipping.")
        return

    n_zones = len(zones)
    infiltration_per_zone = infiltration_m3_s_total / n_zones
    vent_per_zone = vent_flow_m3_s_total / n_zones

    print(
        f"[VENTILATION] Bldg {bldg_id}, sys={system_type}, "
        f"infiltration={infiltration_m3_s_total:.3f}, vent={vent_flow_m3_s_total:.3f}"
    )

    # 7) Create infiltration & ventilation objects per zone
    for zone_obj in zones:
        zone_name = zone_obj.Name

        # system_type + pick_strategy chosen from assigned_vent
        # infiltration_sched_name & ventilation_sched_name come from assigned_vent
        iobj, vobj = create_ventilation_system(
            idf,
            building_function=bldg_func,
            system_type=system_type,
            zone_name=zone_name,
            infiltration_m3_s=infiltration_per_zone,
            vent_flow_m3_s=vent_per_zone,
            infiltration_sched_name=infiltration_sched,
            ventilation_sched_name=ventilation_sched,
            pick_strategy="random" if strategy == "B" else "midpoint"
        )

        print(
            f"   => {zone_name} infiltration={infiltration_per_zone:.4f} "
            f"vent={vent_per_zone:.4f}"
        )

    # 8) If system_type == "D", set HRV effectiveness on IdealLoads
    if system_type == "D" and hrv_eff > 0.0:
        for zone_obj in zones:
            zone_name = zone_obj.Name
            ideal_name = f"{zone_name} Ideal Loads"
            ideal_obj = idf.getobject("ZONEHVAC:IDEALLOADSAIRSYSTEM", ideal_name)
            if ideal_obj:
                # If the IDD fields exist, set them (E+ >=9.0 field name).
                if hasattr(ideal_obj, "Sensible_Heat_Recovery_Effectiveness"):
                    ideal_obj.Sensible_Heat_Recovery_Effectiveness = hrv_eff
                    print(f"   => {ideal_name} HRV eff set to {hrv_eff:.3f}")

                # Example: if you also want to set Latent:
                # if hasattr(ideal_obj, "Latent_Heat_Recovery_Effectiveness"):
                #     ideal_obj.Latent_Heat_Recovery_Effectiveness = 0.0
            else:
                print(f"[VENT WARNING] {zone_name} Ideal Loads not found for system D. Skipping HRV eff.")

    return
