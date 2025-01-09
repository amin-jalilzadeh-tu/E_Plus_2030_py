# fenez/fenestration.py

def add_fenestration(
    idf,
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
    1) Retrieve the final WWR using assign_fenestration_parameters(...).
    2) Remove existing FENESTRATIONSURFACE:DETAILED from the IDF.
    3) Use geomeppy's IDF.set_wwr(...) to add new window surfaces
       referencing a known "Window1C" construction (created by your materials.py).
    """

    from geomeppy import IDF as GeppyIDF
    from .assign_fenestration_values import assign_fenestration_parameters

    # 1) Compute or retrieve final WWR
    wwr = assign_fenestration_parameters(
        building_row=building_row,
        scenario=scenario,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config_fenez=user_config_fenez,    # <-- Pass in override config
        assigned_fenez_log=assigned_fenez_log,
        use_computed_wwr=use_computed_wwr,
        include_doors_in_wwr=include_doors_in_wwr
    )

    # 2) Remove any existing fenestration objects
    fenestrations = idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]
    del fenestrations[:]  # Clear list

    # 3) Use geomeppy's set_wwr(...) to create new window surfaces
    #    We assume a "Window1C" construction is already defined in your materials
    GeppyIDF.set_wwr(idf, wwr=wwr, construction="Window1C")

    print(f"[add_fenestration] Building: {building_row.get('ogc_fid','?')} => WWR={wwr:.3f}, used Window1C")
