# Elec/lighting.py

from .assign_lighting_values import assign_lighting_parameters
from .schedules import create_lighting_schedule, create_parasitic_schedule

def get_building_category_and_subtype(building_row):
    """
    Returns (building_category, sub_type) strings based on building_row.
    Adjust the logic as needed, depending on how your CSV or DB fields
    are structured.

    Example:
      - If building_row["building_function"] is "Residential" or "Non-Residential",
        we treat that as the high-level category.
      - For sub_type, we might read "Corner House", "Office Function", etc.

    If the row does not have enough detail, we fallback to a default.
    """
    # Try to get building_category directly
    building_category = building_row.get("building_category", "").strip()
    sub_type = building_row.get("building_subtype", "").strip()

    # If empty, fallback to building_function
    if not building_category:
        func = building_row.get("building_function", "").lower()
        if "resid" in func:    # e.g. "residential"
            building_category = "Residential"
        else:
            building_category = "Non-Residential"

    # If sub_type was not set, try to read from building_function
    # or default to "Other Use Function"
    if not sub_type:
        sub_type_candidate = building_row.get("building_function", "").strip()
        # If it's obviously one of your sub-types, use it:
        if sub_type_candidate in [
            "Corner House", "Apartment", "Terrace or Semi-detached House",
            "Detached House", "Two-and-a-half-story House",
            "Meeting Function", "Healthcare Function", "Sport Function",
            "Cell Function", "Retail Function", "Industrial Function",
            "Accommodation Function", "Office Function",
            "Education Function", "Other Use Function"
        ]:
            sub_type = sub_type_candidate
        else:
            # Fallback if not recognized
            sub_type = "Other Use Function"

    return building_category, sub_type

    """
    1) Determine building_category (Residential/Non-Residential) and sub_type
       (e.g., "Office Function", "Corner House", etc.).
    2) Retrieve assigned lighting parameters (lights_wm2, parasitic_wm2, tD, tN).
    3) Create schedules in IDF:
       - A lighting schedule with weekday/weekend blocks (create_lighting_schedule).
       - An always-on parasitic schedule (create_parasitic_schedule).
    4) Add LIGHTS/ELECTRICEQUIPMENT objects to each zone in the IDF.

    :param idf: Eppy IDF object or similar
    :param building_row: dict with building data (building_function, etc.)
    :param calibration_stage: "pre_calibration" or "post_calibration"
    :param strategy: "A" (midpoint) or "B" (random selection) for picking from range
    :param random_seed: optional, for reproducible random
    :param user_config: optional override table
    :param assigned_values_log: optional dict to store final picks
    """

def add_lights_and_parasitics(
    idf,
    building_row,
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config=None,
    assigned_values_log=None,
    zonelist_name="ALL_ZONES"   # <--- new parameter for convenience
):
    """
    1) Determine building_category (Residential/Non-Residential) and sub_type.
    2) Retrieve assigned lighting parameters (lights_wm2, parasitic_wm2, tD, tN).
    3) Create schedules in IDF:
       - A lighting schedule with weekday/weekend blocks
       - An always-on parasitic schedule
    4) Add LIGHTS/ELECTRICEQUIPMENT objects referencing a ZoneList in the IDF
       (instead of creating them per Zone).
    """

    # 1) Get building_category / sub_type
    building_category, sub_type = get_building_category_and_subtype(building_row)

    # 2) Retrieve lighting parameters
    bldg_id = int(building_row.get("ogc_fid", 0))

    params = assign_lighting_parameters(
        building_id=bldg_id,
        building_type=sub_type,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config=user_config,
        assigned_log=assigned_values_log
    )

    lights_wm2 = params["lights_wm2"]
    parasitic_wm2 = params["parasitic_wm2"]
    tD = params["tD"]
    tN = params["tN"]

    # 3) Create schedules
    lights_sched_name = create_lighting_schedule(
        idf,
        building_category=building_category,
        sub_type=sub_type,
        schedule_name="LightsSchedule"
    )
    paras_sched_name = create_parasitic_schedule(idf, sched_name="ParasiticSchedule")

    # 4) Reference the existing ZoneList instead of looping through each zone.
    #
    #    Make sure `create_zonelist(idf, "ALL_ZONES")` has been called
    #    *before* calling this function, so that zonelist_name is valid.
    #
    #    Add a single LIGHTS object for the entire ZoneList:
    lights_obj = idf.newidfobject("LIGHTS")
    lights_obj.Name = f"Lights_{zonelist_name}"
    lights_obj.Zone_or_ZoneList_or_Space_or_SpaceList_Name = zonelist_name
    lights_obj.Schedule_Name = lights_sched_name
    lights_obj.Design_Level_Calculation_Method = "Watts/Area"
    lights_obj.Watts_per_Zone_Floor_Area = lights_wm2
    lights_obj.Fraction_Radiant = 0.7
    lights_obj.Fraction_Visible = 0.2
    lights_obj.Fraction_Replaceable = 1.0

    #    And a single ELECTRICEQUIPMENT object for parasitic loads:
    eq_obj = idf.newidfobject("ELECTRICEQUIPMENT")
    eq_obj.Name = f"Lighting_Parasitic_{zonelist_name}"
    eq_obj.Zone_or_ZoneList_or_Space_or_SpaceList_Name = zonelist_name
    eq_obj.Schedule_Name = paras_sched_name
    eq_obj.Design_Level_Calculation_Method = "Watts/Area"
    eq_obj.Watts_per_Zone_Floor_Area = parasitic_wm2
    eq_obj.Fraction_Radiant = 0.0
    eq_obj.Fraction_Lost = 1.0

    # Optionally return references to the newly created objects
    return lights_obj, eq_obj