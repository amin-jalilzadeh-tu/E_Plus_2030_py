# DHW/water_heater.py

from .assign_dhw_values import assign_dhw_parameters
from .parameters import calculate_dhw_parameters
from .schedules import create_dhw_schedules

def add_dhw_to_idf(
    idf,
    building_row,
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    name_suffix="MyDHW",
    user_config_dhw=None,
    assigned_dhw_log=None,
    use_nta=False
):
    """
    1) Retrieve 'dhw_key' directly from building_row (or use a fallback).
    2) Pull parameter ranges from dhw_lookup (or fallback).
    3) Merge with user_config_dhw if any.
    4) Calculate occupant_count, daily usage, peak flow, etc.
    5) Create schedules, then WaterHeater:Mixed object in the IDF.
    """

    # 1) Obtain the building's dhw_key from building_row, or fallback:
    #    e.g. if building_row["dhw_key"] might be "Apartment", "Detached House",
    #         "Office Function", etc.
    dhw_building_key = building_row.get("dhw_key", "Detached House")
    bldg_id = building_row.get("ogc_fid", 0)  # or your building ID field

    # 2) Assign from dhw_lookup, with user config overrides
    assigned = assign_dhw_parameters(
        building_id=bldg_id,
        dhw_key=dhw_building_key,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_dhw=user_config_dhw,
        assigned_dhw_log=assigned_dhw_log,
        building_row=building_row,
        use_nta=use_nta
    )

    # occupant_count if present
    occupant_count = building_row.get("occupant_count", None)
    floor_area_m2 = building_row.get("floor_area_m2", building_row.get("area", None))

    # 3) Calculate final numeric parameters (occupant_count, daily liters, etc.)
    params = calculate_dhw_parameters(
        assigned,
        floor_area_m2=floor_area_m2,
        occupant_count=occupant_count
    )

    # 4) Build schedules for use fraction & setpoint
    frac_sched_name, setpoint_sched_name = create_dhw_schedules(
        idf,
        schedule_name_suffix=name_suffix,
        setpoint_c=params["setpoint_c"],
        morning_val=assigned["sched_morning"],
        peak_val=assigned["sched_peak"],
        afternoon_val=assigned["sched_afternoon"],
        evening_val=assigned["sched_evening"]
    )

    # 5) Create the WaterHeater:Mixed object
    wh_name = f"{name_suffix}_WaterHeater"

    # Example logic for selecting fuel type & heater efficiency:
    # if the chosen dhw_key name includes "Residential", assume electricity, else gas
    # or you can do something like: "if 'Function' in dhw_key => Non-Residential"
    if "Function" in dhw_building_key:
        fuel_type = "NaturalGas"
        heater_eff = 0.8
    else:
        fuel_type = "Electricity"
        heater_eff = 0.9

    wh_obj = idf.newidfobject(
        "WATERHEATER:MIXED",
        Name=wh_name,
        Tank_Volume=params["tank_volume_m3"],
        Setpoint_Temperature_Schedule_Name=setpoint_sched_name,
        Deadband_Temperature_Difference=2.0,
        Maximum_Temperature_Limit=80.0,
        Heater_Control_Type="CYCLE",
        Heater_Maximum_Capacity=params["heater_capacity_w"],
        Heater_Fuel_Type=fuel_type,
        Heater_Thermal_Efficiency=heater_eff,
        Off_Cycle_Parasitic_Fuel_Consumption_Rate=0.0,
        Off_Cycle_Parasitic_Fuel_Type="Electricity",
        Off_Cycle_Parasitic_Heat_Fraction_to_Tank=0.0,
        On_Cycle_Parasitic_Fuel_Consumption_Rate=0.0,
        On_Cycle_Parasitic_Fuel_Type="Electricity",
        On_Cycle_Parasitic_Heat_Fraction_to_Tank=0.0,
        Ambient_Temperature_Indicator="SCHEDULE",
        Ambient_Temperature_Schedule_Name="Always22C",
        Off_Cycle_Loss_Coefficient_to_Ambient_Temperature=5.0,
        On_Cycle_Loss_Coefficient_to_Ambient_Temperature=5.0,
        Peak_Use_Flow_Rate=params["peak_flow_m3s"],
        Use_Flow_Rate_Fraction_Schedule_Name=frac_sched_name
    )

    # Optional debug prints
    print(f"[DHW] building_id={bldg_id}, dhw_key={dhw_building_key}")
    print(f"     occupant_count={params['occupant_count']} daily_liters={params['daily_liters']:.1f}")
    print(f"     setpoint={params['setpoint_c']:.1f} C, tank_volume={params['tank_volume_m3']:.3f} m³")
    print(f"     schedules => {frac_sched_name}, {setpoint_sched_name}")

    return wh_obj
