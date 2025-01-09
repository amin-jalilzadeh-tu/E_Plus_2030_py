# fenez/dict_override_excel.py

import pandas as pd
import copy
import math

def override_dictionaries_from_excel(
    excel_path,
    default_res_data,
    default_nonres_data,
    default_roughness="MediumRough",
    fallback_wwr_range=(0.2, 0.3)
):
    """
    Reads an Excel file containing envelope data (including min_wwr, max_wwr, 
    calibration_stage, etc.) and uses it to override or extend the default 
    dictionaries for residential and non_residential materials.

    Parameters
    ----------
    excel_path : str
        Path to the Excel file, e.g. 'D:\\Documents\\E_Plus_2027_py\\envelop.xlsx'
    default_res_data : dict
        The original residential_materials_data dictionary
    default_nonres_data : dict
        The original non_residential_materials_data dictionary
    default_roughness : str
        Fallback roughness if none is provided in the Excel
    fallback_wwr_range : tuple
        Fallback WWR range (min, max) if Excel does not specify

    Returns
    -------
    new_res_data : dict
        Updated residential data dictionary
    new_nonres_data : dict
        Updated non-residential data dictionary

    Notes
    -----
    - The Excel must contain certain columns:
        building_function, building_type, year_range, scenario, calibration_stage,
        element, area_m2, R_value_min, R_value_max, U_value_min, U_value_max,
        roughness, material_opaque_lookup, material_window_lookup, min_wwr, max_wwr
    - Rows with building_function='residential' will override entries in 
      residential_materials_data; rows with 'non_residential' override non_res.
    - You can add or remove elements (like 'doors', 'windows', 'walls', etc.) 
      by specifying the 'element' column.
    """

    # Make deep copies so we don't mutate the originals
    new_res_data = copy.deepcopy(default_res_data)
    new_nonres_data = copy.deepcopy(default_nonres_data)

    # Load Excel
    df = pd.read_excel(excel_path)

    # Ensure expected columns exist
    required_cols = [
        "building_function",
        "building_type",
        "year_range",
        "scenario",
        "calibration_stage",
        "element",
        "area_m2",
        "R_value_min",
        "R_value_max",
        "U_value_min",
        "U_value_max",
        "roughness",
        "material_opaque_lookup",
        "material_window_lookup",
        "min_wwr",
        "max_wwr"
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Excel file is missing required columns: {missing_cols}")

    # Go row by row and override
    for _, row in df.iterrows():
        bfunc = str(row["building_function"]).strip().lower()  # 'residential' or 'non_residential'
        btype = str(row["building_type"]).strip()
        yrange = str(row["year_range"]).strip()
        scen   = str(row["scenario"]).strip()
        stage  = str(row["calibration_stage"]).strip()

        # Decide which dictionary to modify
        if bfunc == "residential":
            current_dict = new_res_data
        else:
            current_dict = new_nonres_data

        dict_key = (btype, yrange, scen, stage)

        # Create or fetch the entry
        if dict_key not in current_dict:
            current_dict[dict_key] = {
                "roughness": default_roughness,
                "wwr_range": fallback_wwr_range
            }
        data_entry = current_dict[dict_key]

        # Possibly override the top-level roughness
        rough_val = str(row["roughness"]).strip()
        if rough_val.lower() != "nan":
            data_entry["roughness"] = rough_val

        # Possibly override the top-level wwr_range if we have min_wwr & max_wwr
        if not pd.isna(row["min_wwr"]) and not pd.isna(row["max_wwr"]):
            min_wwr = float(row["min_wwr"])
            max_wwr = float(row["max_wwr"])
            data_entry["wwr_range"] = (min_wwr, max_wwr)

        # Now handle the sub-element (doors, ground_floor, windows, etc.)
        elem_name = str(row["element"]).strip()
        if elem_name not in data_entry:
            data_entry[elem_name] = {}

        elem_dict = data_entry[elem_name]

        # area
        if not pd.isna(row["area_m2"]):
            elem_dict["area_m2"] = float(row["area_m2"])

        # R_value_range
        rmin = row["R_value_min"]
        rmax = row["R_value_max"]
        if not pd.isna(rmin) and not pd.isna(rmax):
            elem_dict["R_value_range"] = (float(rmin), float(rmax))

        # U_value_range
        umin = row["U_value_min"]
        umax = row["U_value_max"]
        if not pd.isna(umin) and not pd.isna(umax):
            elem_dict["U_value_range"] = (float(umin), float(umax))

        # Overwrite or store roughness for that element if you want (optional):
        elem_dict["roughness"] = data_entry["roughness"]

        # material_opaque_lookup
        opq_lookup = row["material_opaque_lookup"]
        if pd.notna(opq_lookup):
            elem_dict["material_opaque_lookup"] = str(opq_lookup).strip()

        # material_window_lookup
        win_lookup = row["material_window_lookup"]
        if pd.notna(win_lookup):
            elem_dict["material_window_lookup"] = str(win_lookup).strip()

    return new_res_data, new_nonres_data
