# fenez/materials.py

from geomeppy import IDF
from .materials_config import get_extended_materials_data

def _store_material_picks(assigned_fenez_log, building_id, label, mat_data):
    """
    A helper to store final material picks in assigned_fenez_log[building_id][label].
    Skips any keys that end with '_range'.
    E.g. label might be 'top_opq' or 'top_win' or 'element_floor', etc.
    """
    if not mat_data:
        return

    # Only store final picks (no ranges)
    filtered = {}
    for k, v in mat_data.items():
        if k.endswith("_range"):
            continue
        filtered[k] = v

    if building_id not in assigned_fenez_log:
        assigned_fenez_log[building_id] = {}

    # Example: store under assigned_fenez_log[1234]["fenez_top_opq"] = {...}
    assigned_fenez_log[building_id][f"fenez_{label}"] = filtered


def update_construction_materials(
    idf,
    building_row,
    scenario="scenario1",
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config_fenez=None,
    assigned_fenez_log=None
):
    """
    1) Calls get_extended_materials_data(...) => returns a dict with final picks 
       (no longer just ranges).
    2) Removes all existing Materials & Constructions from the IDF (clean slate).
    3) Creates new Opaque & Window materials (if present), plus multiple named Constructions.
    4) Logs assigned final picks (no range) into assigned_fenez_log if provided.
    """

    # 1) Identify building function & type
    bldg_func = building_row.get("building_function", "residential")
    if bldg_func.lower() == "residential":
        bldg_type = building_row.get("residential_type", "")
    else:
        bldg_type = building_row.get("non_residential_type", "")

    age_range = building_row.get("age_range", "2015 and later")
    building_id = building_row.get("ogc_fid", None)  # or "pand_id" if that is the ID

    # 2) Retrieve extended materials data
    data = get_extended_materials_data(
        building_function=bldg_func,
        building_type=bldg_type,
        age_range=age_range,
        scenario=scenario,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_fenez=user_config_fenez
    )

    mat_opq = data.get("material_opaque", None)
    mat_win = data.get("material_window", None)

    # If logging final picks, store them now, skipping _range
    if assigned_fenez_log is not None and building_id is not None:
        # Store top-level opaque material
        _store_material_picks(
            assigned_fenez_log=assigned_fenez_log,
            building_id=building_id,
            label="top_opq",
            mat_data=mat_opq
        )
        # Store top-level window material
        _store_material_picks(
            assigned_fenez_log=assigned_fenez_log,
            building_id=building_id,
            label="top_win",
            mat_data=mat_win
        )

        # Also store final picks for sub-elements if you want them all in the CSV
        for elem_name, elem_data in data.get("elements", {}).items():
            # If there's a "material_opaque" or "material_window" inside an element
            opq_sub = elem_data.get("material_opaque", None)
            win_sub = elem_data.get("material_window", None)

            _store_material_picks(
                assigned_fenez_log=assigned_fenez_log,
                building_id=building_id,
                label=f"{elem_name}_opq",
                mat_data=opq_sub
            )
            _store_material_picks(
                assigned_fenez_log=assigned_fenez_log,
                building_id=building_id,
                label=f"{elem_name}_win",
                mat_data=win_sub
            )

            # Also store final numeric R_value or U_value, area, etc., if present
            # (We do it under the same dictionary in assigned_fenez_log)
            # For instance:
            if elem_data.get("R_value") is not None:
                assigned_fenez_log[building_id][f"fenez_{elem_name}_R_value"] = elem_data["R_value"]
            if elem_data.get("U_value") is not None:
                assigned_fenez_log[building_id][f"fenez_{elem_name}_U_value"] = elem_data["U_value"]
            if elem_data.get("area_m2") is not None:
                assigned_fenez_log[building_id][f"fenez_{elem_name}_area_m2"] = elem_data["area_m2"]

    # 3) Remove existing Materials & Constructions in the IDF
    for obj_type in [
        "MATERIAL",
        "MATERIAL:NOMASS",
        "WINDOWMATERIAL:GLAZING",
        "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM",
        "CONSTRUCTION"
    ]:
        for obj in idf.idfobjects[obj_type][:]:
            idf.removeidfobject(obj)

    # The rest is unchanged from your earlier code, creating new Material/Construction objects:

    opq_name = None
    win_name = None

    # Create Opaque Material
    if mat_opq:
        obj_type = mat_opq["obj_type"].upper()
        if obj_type == "MATERIAL":
            mat_obj = idf.newidfobject("MATERIAL")
            mat_obj.Name = mat_opq["Name"]
            mat_obj.Roughness = mat_opq["Roughness"]
            mat_obj.Thickness = mat_opq["Thickness"]
            mat_obj.Conductivity = mat_opq["Conductivity"]
            mat_obj.Density = mat_opq["Density"]
            mat_obj.Specific_Heat = mat_opq["Specific_Heat"]
            mat_obj.Thermal_Absorptance = mat_opq["Thermal_Absorptance"]
            mat_obj.Solar_Absorptance   = mat_opq["Solar_Absorptance"]
            mat_obj.Visible_Absorptance = mat_opq["Visible_Absorptance"]
            opq_name = mat_obj.Name

        elif obj_type == "MATERIAL:NOMASS":
            mat_obj = idf.newidfobject("MATERIAL:NOMASS")
            mat_obj.Name = mat_opq["Name"]
            mat_obj.Roughness = mat_opq["Roughness"]
            mat_obj.Thermal_Resistance = mat_opq["Thermal_Resistance"]
            mat_obj.Thermal_Absorptance = mat_opq["Thermal_Absorptance"]
            mat_obj.Solar_Absorptance   = mat_opq["Solar_Absorptance"]
            mat_obj.Visible_Absorptance = mat_opq["Visible_Absorptance"]
            opq_name = mat_obj.Name

    # Create Window Material
    if mat_win:
        wtype = mat_win["obj_type"].upper()
        if wtype == "WINDOWMATERIAL:GLAZING":
            wmat = idf.newidfobject("WINDOWMATERIAL:GLAZING")
            wmat.Name = mat_win["Name"]
            wmat.Optical_Data_Type = mat_win["Optical_Data_Type"]
            wmat.Thickness = mat_win["Thickness"]
            wmat.Solar_Transmittance_at_Normal_Incidence = mat_win["Solar_Transmittance"]
            wmat.Front_Side_Solar_Reflectance_at_Normal_Incidence = mat_win["Front_Solar_Reflectance"]
            wmat.Back_Side_Solar_Reflectance_at_Normal_Incidence  = mat_win["Back_Solar_Reflectance"]
            wmat.Visible_Transmittance_at_Normal_Incidence        = mat_win["Visible_Transmittance"]
            wmat.Front_Side_Visible_Reflectance_at_Normal_Incidence = mat_win["Front_Visible_Reflectance"]
            wmat.Back_Side_Visible_Reflectance_at_Normal_Incidence  = mat_win["Back_Visible_Reflectance"]
            wmat.Infrared_Transmittance_at_Normal_Incidence         = mat_win["IR_Transmittance"]
            wmat.Front_Side_Infrared_Hemispherical_Emissivity       = mat_win["Front_IR_Emissivity"]
            wmat.Back_Side_Infrared_Hemispherical_Emissivity        = mat_win["Back_IR_Emissivity"]
            wmat.Conductivity = mat_win["Conductivity"]
            wmat.Dirt_Correction_Factor_for_Solar_and_Visible_Transmittance = mat_win["Dirt_Correction_Factor"]
            wmat.Solar_Diffusing = mat_win["Solar_Diffusing"]
            win_name = wmat.Name

        elif wtype == "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM":
            wmat = idf.newidfobject("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM")
            wmat.Name = mat_win["Name"]
            # If you have UFactor/SHGC in mat_win, set them as well
            win_name = wmat.Name

    # Create Constructions
    if opq_name:
        # Exterior walls
        c_ext = idf.newidfobject("CONSTRUCTION")
        c_ext.Name = "Ext_Walls1C"
        c_ext.Outside_Layer = opq_name
        # ... similarly for interior walls, adiabatic walls, roof, ceiling, ground floor, etc.
        c_int = idf.newidfobject("CONSTRUCTION")
        c_int.Name = "Int_Walls1C"
        c_int.Outside_Layer = opq_name

        c_adiab = idf.newidfobject("CONSTRUCTION")
        c_adiab.Name = "Adiabatic_Walls1C"
        c_adiab.Outside_Layer = opq_name

        c_roof = idf.newidfobject("CONSTRUCTION")
        c_roof.Name = "Roof1C"
        c_roof.Outside_Layer = opq_name

        c_ceil = idf.newidfobject("CONSTRUCTION")
        c_ceil.Name = "Ceiling1C"
        c_ceil.Outside_Layer = opq_name

        c_grnd = idf.newidfobject("CONSTRUCTION")
        c_grnd.Name = "GroundFloor1C"
        c_grnd.Outside_Layer = opq_name

        c_ifloor = idf.newidfobject("CONSTRUCTION")
        c_ifloor.Name = "IntFloor1C"
        c_ifloor.Outside_Layer = opq_name

    if win_name:
        c_win = idf.newidfobject("CONSTRUCTION")
        c_win.Name = "Window1C"
        c_win.Outside_Layer = win_name

    print(f"[update_construction_materials] Created Opaque Material={opq_name}, "
          f"Window Material={win_name}")
    print("=> Constructions created: Ext_Walls1C, Int_Walls1C, Adiabatic_Walls1C, Roof1C, "
          "Ceiling1C, GroundFloor1C, IntFloor1C (if opq), and Window1C (if window).")


def assign_constructions_to_surfaces(idf):
    """
    Assign each BUILDINGSURFACE:DETAILED to a suitable construction name
    depending on Surface_Type and Outside_Boundary_Condition.
    """

    for surface in idf.idfobjects["BUILDINGSURFACE:DETAILED"]:
        s_type = surface.Surface_Type.upper()
        bc = surface.Outside_Boundary_Condition.upper()

        if s_type == "WALL":
            if bc == "OUTDOORS":
                surface.Construction_Name = "Ext_Walls1C"
            elif bc == "SURFACE":
                surface.Construction_Name = "Int_Walls1C"
            elif bc == "ADIABATIC":
                surface.Construction_Name = "Adiabatic_Walls1C"
            else:
                surface.Construction_Name = "Ext_Walls1C"

        elif s_type == "ROOF":
            surface.Construction_Name = "Roof1C"

        elif s_type == "CEILING":
            surface.Construction_Name = "Ceiling1C"

        elif s_type == "FLOOR":
            if bc == "GROUND":
                surface.Construction_Name = "GroundFloor1C"
            elif bc in ["ADIABATIC", "SURFACE"]:
                surface.Construction_Name = "IntFloor1C"
            else:
                surface.Construction_Name = "GroundFloor1C"

        else:
            surface.Construction_Name = "Ext_Walls1C"

    # If not using geomeppy's set_wwr(...) to define fenestration surfaces,
    # you could also set fenestration surfaces' construction here:
    for fen in idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]:
        fen.Construction_Name = "Window1C"

    print("[assign_constructions_to_surfaces] => Surfaces assigned.")
