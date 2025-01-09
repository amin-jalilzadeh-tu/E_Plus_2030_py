# epw/run_epw_sims.py

import os
import logging
from eppy.modeleditor import IDF
from multiprocessing import Pool

from .assign_epw_file import assign_epw_for_building_with_overrides

def run_simulation(args):
    """
    :param args: tuple (idf_path, epwfile, iddfile, output_directory, building_index)
    """
    idf_path, epwfile, iddfile, output_directory, bldg_idx = args
    try:
        # Set up IDF
        IDF.setiddname(iddfile)
        idf = IDF(idf_path, epwfile)

        # Build run options
        os.makedirs(output_directory, exist_ok=True)
        # e.g. simulation_bldg0 => identifies building 0 inside the year folder
        run_opts = {
            "output_prefix": f"simulation_bldg{bldg_idx}",
            "output_suffix": "C",
            "output_directory": output_directory,
            "readvars": True,
            "expandobjects": True
        }

        # Execute
        idf.run(**run_opts)
        logging.info(f"[run_simulation] OK: {idf_path} (Bldg {bldg_idx}) with EPW {epwfile} -> {output_directory}")
    except Exception as e:
        logging.error(f"[run_simulation] Error for building {bldg_idx} with {idf_path} & {epwfile}: {e}",
                      exc_info=True)


    """
    Yields (idf_path, epwfile, iddfile, output_directory, building_index) 
    for each building row, grouping by 'desired_climate_year'.

    :param df_buildings: DataFrame with columns lat, lon, desired_climate_year, idf_name, etc.
    :param idf_directory: folder containing the final .idf files
    :param iddfile: path to your EnergyPlus .idd
    :param base_output_dir: top-level folder for results
    """

def generate_simulations(
    df_buildings,
    idf_directory,
    iddfile,
    base_output_dir,
    user_config_epw=None,       # <--- pass config
    assigned_epw_log=None       # <--- pass log
):
    for idx, row in df_buildings.iterrows():
        # pick EPW
        epw_path = assign_epw_for_building_with_overrides(
            building_row=row,
            user_config_epw=user_config_epw,
            assigned_epw_log=assigned_epw_log
        )
        if not epw_path:
            logging.warning(f"No EPW found for building idx={idx}, skipping.")
            continue

        # rest of logic is the same
        idf_name = row.get("idf_name")
        if not idf_name:
            logging.warning(f"No 'idf_name' for building idx={idx}, skipping.")
            continue

        idf_path = os.path.join(idf_directory, idf_name)
        if not os.path.isfile(idf_path):
            logging.warning(f"IDF not found: {idf_path}, skipping building idx={idx}.")
            continue

        year = row.get("desired_climate_year", 2020)
        output_dir = os.path.join(base_output_dir, str(year))

        yield (idf_path, epw_path, iddfile, output_dir, idx)

def simulate_all(
    df_buildings,
    idf_directory,
    iddfile,
    base_output_dir,
    user_config_epw=None,       # <--- new
    assigned_epw_log=None,      # <--- new
    num_workers=4
):
    """
    Runs E+ simulations in parallel:
      - For each row in df_buildings, we pick an EPW & IDF.
      - Group results by year so all building results for year X go in base_output_dir/X.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("[simulate_all] Starting...")

    tasks = list(
        generate_simulations(
            df_buildings,
            idf_directory,
            iddfile,
            base_output_dir,
            user_config_epw=user_config_epw,
            assigned_epw_log=assigned_epw_log
        )
    )



    if not tasks:
        logging.warning("[simulate_all] No tasks to run. Exiting.")
        return

    logging.info(f"[simulate_all] Found {len(tasks)} tasks. Using {num_workers} workers.")
    with Pool(num_workers) as pool:
        pool.map(run_simulation, tasks)

    logging.info("[simulate_all] All simulations complete.")