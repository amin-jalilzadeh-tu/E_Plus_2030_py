# DHW/parameters.py

def calculate_dhw_parameters(
    assigned: dict,
    floor_area_m2: float = None,
    occupant_count: int = None
):
    """
    assigned = {
       "occupant_density_m2_per_person": ...,
       "liters_per_person_per_day": ...,
       "default_tank_volume_liters": ...,
       "default_heater_capacity_w": ...,
       "setpoint_c": ...,
       "usage_split_factor": ...,
       "peak_hours": ...
    }
    Compute occupant_count, daily liters, flow, etc.
    """

    occupant_density = assigned["occupant_density_m2_per_person"]
    liters_per_person = assigned["liters_per_person_per_day"]
    tank_liters = assigned["default_tank_volume_liters"]
    heater_w = assigned["default_heater_capacity_w"]
    setpoint_c = assigned["setpoint_c"]
    usage_split_factor = assigned["usage_split_factor"]
    peak_hours = assigned["peak_hours"]

    # 1) occupant_count
    if occupant_count is None:
        if occupant_density and floor_area_m2:
            occupant_count = floor_area_m2 / occupant_density
        else:
            occupant_count = 4  # fallback
    occupant_count = int(round(occupant_count))

    # 2) daily liters
    daily_liters = occupant_count * liters_per_person

    # 3) daily m³
    daily_m3 = daily_liters / 1000.0

    # 4) peak flow
    if peak_hours > 0:
        peak_flow_m3s = (daily_m3 * usage_split_factor) / (peak_hours * 3600.0)
    else:
        peak_flow_m3s = daily_m3 / (24.0 * 3600.0)

    # 5) tank volume (m3)
    tank_volume_m3 = tank_liters / 1000.0

    return {
        "occupant_count": occupant_count,
        "daily_liters": daily_liters,
        "peak_flow_m3s": peak_flow_m3s,
        "tank_volume_m3": tank_volume_m3,
        "heater_capacity_w": heater_w,
        "setpoint_c": setpoint_c
    }
