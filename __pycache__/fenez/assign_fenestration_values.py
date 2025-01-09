# fenez/assign_fenestration_values.py

from .materials_config import (
    get_extended_materials_data,
    compute_wwr
)

def assign_fenestration_parameters(
    building_row,
    scenario="scenario1",
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config_fenez=None,
    assigned_fenez_log=None,
    use_computed_wwr=False,
    include_doors_in_wwr=False
):
    """
    1) Calls get_extended_materials_data(...), which picks a final 'wwr' from wwr_range,
       plus all material data.
    2) If use_computed_wwr => override that final WWR from the 'elements' dictionary (windows/doors).
    3) Store final WWR (and its range) in assigned_fenez_log if provided.
    4) Return final WWR as a single float.
    """

    bldg_func = building_row.get("building_function", "residential")
    if bldg_func.lower() == "residential":
        building_type = building_row.get("residential_type", "UnknownHouseType")
    else:
        building_type = building_row.get("non_residential_type", "UnknownNonResType")

    age_range = building_row.get("age_range", "2015 and later")
    building_id = building_row.get("ogc_fid", None)

    # (A) Retrieve extended data from materials_config
    data = get_extended_materials_data(
        building_function=bldg_func,
        building_type=building_type,
        age_range=age_range,
        scenario=scenario,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_fenez=user_config_fenez,
        assigned_fenez_log=assigned_fenez_log,  # <--- pass the log so we store ranges for wwr, materials
    )

    # (B) data["wwr"] is the final WWR from picking wwr_range
    # if use_computed_wwr => override
    if not use_computed_wwr:
        final_wwr = data["wwr"]
    else:
        elements_dict = data.get("elements", {})
        final_wwr = compute_wwr(elements_dict, include_doors=include_doors_in_wwr)

    # (C) If assigned_fenez_log => store the final WWR under e.g. "fenez_wwr"
    if assigned_fenez_log is not None and building_id is not None:
        if building_id not in assigned_fenez_log:
            assigned_fenez_log[building_id] = {}
        # We already stored the wwr_range in get_extended_materials_data (see below).
        # So here we just finalize the actual WWR if it's overridden by `use_computed_wwr`
        assigned_fenez_log[building_id]["fenez_wwr"] = final_wwr

    return final_wwr
