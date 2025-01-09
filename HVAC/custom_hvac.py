# HVAC/custom_hvac.py

from .assign_hvac_values import assign_hvac_ideal_parameters

def add_HVAC_Ideal_to_all_zones(
    idf,
    building_row=None,
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config_hvac=None,
    assigned_hvac_log=None
):
    """
    Adds an Ideal Loads Air System to every Zone in the IDF,
    along with schedules & setpoints derived from hvac_lookup ranges
    and user_config_hvac overrides.

    1) We now pass additional fields from building_row
       (residential_type, non_residential_type, age_range, scenario)
       to the assign_hvac_ideal_parameters function.

    2) The returned hvac_params includes day/night setpoints, supply temps,
       and optionally schedule_details.

    3) We then create or update the IDF schedules and objects as before.
    """

    # Extract new fields (if absent, provide default)
    bldg_id = building_row.get("ogc_fid", 0)

    # building_function => "residential" or "non_residential"
    bldg_func = building_row.get("building_function", "residential")

    # subtypes
    res_type = building_row.get("residential_type", "Two-and-a-half-story House")
    nonres_type = building_row.get("non_residential_type", "Meeting Function")

    # age range => "1900-2000", "2000-2024", etc.
    age_range = building_row.get("age_range", "1900-2000")

    # scenario => "scenario1", "scenario2"
    scenario = building_row.get("scenario", "scenario1")

    # Then proceed:
    hvac_params = assign_hvac_ideal_parameters(
        building_id=bldg_id,
        building_function=bldg_func,
        residential_type=res_type,
        non_residential_type=nonres_type,
        age_range=age_range,
        scenario=scenario,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_hvac=user_config_hvac,
        assigned_hvac_log=assigned_hvac_log
    )
    # e.g., hvac_params["heating_day_setpoint"] => 19.8
    # etc.

    # 2) Create or update your SCHEDULETYPELIMITS if needed
    if not idf.getobject("SCHEDULETYPELIMITS", "Temperature"):
        idf.newidfobject(
            "SCHEDULETYPELIMITS",
            Name="Temperature",
            Lower_Limit_Value=-100,
            Upper_Limit_Value=200,
            Numeric_Type="CONTINUOUS"
        )

    if not idf.getobject("SCHEDULETYPELIMITS", "ControlType"):
        idf.newidfobject(
            "SCHEDULETYPELIMITS",
            Name="ControlType",
            Lower_Limit_Value=0,
            Upper_Limit_Value=4,
            Numeric_Type="DISCRETE"
        )

    # 3) Create or update the Control Type schedule
    if not idf.getobject("SCHEDULE:COMPACT", "ZONE CONTROL TYPE SCHEDULE"):
        sc = idf.newidfobject("SCHEDULE:COMPACT")
        sc.Name = "ZONE CONTROL TYPE SCHEDULE"
        sc.Schedule_Type_Limits_Name = "ControlType"
        sc.Field_1 = "Through: 12/31"
        sc.Field_2 = "For: AllDays"
        sc.Field_3 = "Until: 24:00,4"

    # 4) Build or update the Heating Setpoint schedule.
    #    We'll keep the day from 7:00-19:00 as the 'day' setpoint,
    #    and outside of that as 'night' setpoint. 
    #    You can refine if you want more detail from hvac_params["schedule_details"].

    if not idf.getobject("SCHEDULE:COMPACT", "ZONE HEATING SETPOINTS"):
        sc = idf.newidfobject("SCHEDULE:COMPACT")
        sc.Name = "ZONE HEATING SETPOINTS"
        sc.Schedule_Type_Limits_Name = "Temperature"
        sc.Field_1 = "Through: 12/31"
        sc.Field_2 = "For: AllDays"
        sc.Field_3 = f"Until: 07:00,{hvac_params['heating_night_setpoint']:.2f}"
        sc.Field_4 = f"Until: 19:00,{hvac_params['heating_day_setpoint']:.2f}"
        sc.Field_5 = f"Until: 24:00,{hvac_params['heating_night_setpoint']:.2f}"

    # 5) Build or update the Cooling Setpoint schedule in a similar manner
    if not idf.getobject("SCHEDULE:COMPACT", "ZONE COOLING SETPOINTS"):
        sc = idf.newidfobject("SCHEDULE:COMPACT")
        sc.Name = "ZONE COOLING SETPOINTS"
        sc.Schedule_Type_Limits_Name = "Temperature"
        sc.Field_1 = "Through: 12/31"
        sc.Field_2 = "For: AllDays"
        sc.Field_3 = f"Until: 07:00,{hvac_params['cooling_night_setpoint']:.2f}"
        sc.Field_4 = f"Until: 19:00,{hvac_params['cooling_day_setpoint']:.2f}"
        sc.Field_5 = f"Until: 24:00,{hvac_params['cooling_night_setpoint']:.2f}"

    # 6) Now loop over each zone & create the Ideal Loads & ThermostatSetpoint:DualSetpoint
    for zone_obj in idf.idfobjects["ZONE"]:
        zone_name = zone_obj.Name

        # 6a) Thermostat
        existing_thermo = [
            t for t in idf.idfobjects["ZONECONTROL:THERMOSTAT"]
            if (
                (hasattr(t, "Zone_or_ZoneList_or_Space_or_SpaceList_Name") and
                 getattr(t, "Zone_or_ZoneList_or_Space_or_SpaceList_Name") == zone_name)
                or
                (hasattr(t, "Zone_or_ZoneList_Name") and t.Zone_or_ZoneList_Name == zone_name)
            )
        ]
        if not existing_thermo:
            thermo = idf.newidfobject("ZONECONTROL:THERMOSTAT")
            thermo.Name = f"{zone_name} CONTROLS"

            if hasattr(thermo, "Zone_or_ZoneList_or_Space_or_SpaceList_Name"):
                thermo.Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone_name
            else:
                thermo.Zone_or_ZoneList_Name = zone_name

            thermo.Control_Type_Schedule_Name = "ZONE CONTROL TYPE SCHEDULE"
            thermo.Control_1_Object_Type = "ThermostatSetpoint:DualSetpoint"
            thermo.Control_1_Name = f"{zone_name} SETPOINTS"

            # ThermostatSetpoint:DualSetpoint
            dual = idf.newidfobject("THERMOSTATSETPOINT:DUALSETPOINT")
            dual.Name = f"{zone_name} SETPOINTS"
            dual.Heating_Setpoint_Temperature_Schedule_Name = "ZONE HEATING SETPOINTS"
            dual.Cooling_Setpoint_Temperature_Schedule_Name = "ZONE COOLING SETPOINTS"

        # 6b) EquipmentConnections
        existing_equip_conns = [
            ec for ec in idf.idfobjects["ZONEHVAC:EQUIPMENTCONNECTIONS"]
            if (ec.Zone_Name == zone_name)
        ]
        if not existing_equip_conns:
            eq_conn = idf.newidfobject("ZONEHVAC:EQUIPMENTCONNECTIONS")
            eq_conn.Zone_Name = zone_name
            eq_conn.Zone_Conditioning_Equipment_List_Name = f"{zone_name} EQUIPMENT"
            eq_conn.Zone_Air_Inlet_Node_or_NodeList_Name = f"{zone_name} INLETS"
            eq_conn.Zone_Air_Exhaust_Node_or_NodeList_Name = ""
            eq_conn.Zone_Air_Node_Name = f"{zone_name} NODE"
            eq_conn.Zone_Return_Air_Node_or_NodeList_Name = f"{zone_name} OUTLET"

        # 6c) ZoneHVAC:EquipmentList
        existing_equip_lists = [
            el for el in idf.idfobjects["ZONEHVAC:EQUIPMENTLIST"]
            if (el.Name == f"{zone_name} EQUIPMENT")
        ]
        if not existing_equip_lists:
            eq_list = idf.newidfobject("ZONEHVAC:EQUIPMENTLIST")
            eq_list.Name = f"{zone_name} EQUIPMENT"
            eq_list.Load_Distribution_Scheme = "SequentialLoad"
            eq_list.Zone_Equipment_1_Object_Type = "ZoneHVAC:IdealLoadsAirSystem"
            eq_list.Zone_Equipment_1_Name = f"{zone_name} Ideal Loads"
            eq_list.Zone_Equipment_1_Cooling_Sequence = 1
            eq_list.Zone_Equipment_1_Heating_or_NoLoad_Sequence = 1

        # 6d) Add or update the IdealLoads system
        existing_ideal = [
            ild for ild in idf.idfobjects["ZONEHVAC:IDEALLOADSAIRSYSTEM"]
            if (ild.Name == f"{zone_name} Ideal Loads")
        ]
        if not existing_ideal:
            ideal = idf.newidfobject("ZONEHVAC:IDEALLOADSAIRSYSTEM")
            ideal.Name = f"{zone_name} Ideal Loads"
            ideal.Availability_Schedule_Name = ""  # or "AlwaysOn"
            ideal.Zone_Supply_Air_Node_Name = f"{zone_name} INLETS"
            ideal.Zone_Exhaust_Air_Node_Name = ""
            ideal.System_Inlet_Air_Node_Name = ""
            ideal.Maximum_Heating_Supply_Air_Temperature = hvac_params["max_heating_supply_air_temp"]
            ideal.Minimum_Cooling_Supply_Air_Temperature = hvac_params["min_cooling_supply_air_temp"]
            ideal.Maximum_Heating_Supply_Air_Humidity_Ratio = 0.015
            ideal.Minimum_Cooling_Supply_Air_Humidity_Ratio = 0.009
            ideal.Heating_Limit = "NoLimit"
            ideal.Maximum_Heating_Air_Flow_Rate = "autosize"
            ideal.Cooling_Limit = "NoLimit"
            ideal.Maximum_Cooling_Air_Flow_Rate = "autosize"
            ideal.Dehumidification_Control_Type = "ConstantSupplyHumidityRatio"
            ideal.Humidification_Control_Type = "ConstantSupplyHumidityRatio"
        else:
            # Update if it already exists
            existing_ideal[0].Maximum_Heating_Supply_Air_Temperature = hvac_params["max_heating_supply_air_temp"]
            existing_ideal[0].Minimum_Cooling_Supply_Air_Temperature = hvac_params["min_cooling_supply_air_temp"]

        # 6e) NodeList for supply inlets
        existing_inlet_list = idf.getobject("NODELIST", f"{zone_name} INLETS")
        if not existing_inlet_list:
            nlist = idf.newidfobject("NODELIST")
            nlist.Name = f"{zone_name} INLETS"
            nlist.Node_1_Name = f"{zone_name} INLET"

    # Done
    return
