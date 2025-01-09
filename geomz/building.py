# geomz/building.py

from .assign_geometry_values import assign_geometry_values
from .geometry import compute_dimensions_from_area_perimeter, create_building_base_polygon
from .zoning import create_zones_with_perimeter_depth

def create_building_with_roof_type(
    idf,
    area,
    perimeter,
    orientation,
    building_row,
    edge_types,
    wall_height=None,
    roof_slope_axis='length',
    ridge_position=0.5,
    calibration_stage="pre_calibration",
    strategy="A",
    random_seed=None,
    user_config=None,            # <--- new
    assigned_geom_log=None,       # <--- new
    excel_rules=None  # if you want to pass excel-based geometry overrides

):
    """
    Create building geometry in the IDF.
    We now accept user_config + assigned_geom_log for geometry overrides & logging.
    """

    if wall_height is None:
        # 1) Grab total building height from gem_hoogte (if present)
        gem_hoogte = building_row.get("gem_hoogte", None)
        # 2) Number of floors
        num_floors = building_row.get("gem_bouwlagen", 1)

        if gem_hoogte is not None:
            # If we have a total building height, divide by the number of floors
            total_height = gem_hoogte
        else:
            # If gem_hoogte is missing, assume 3.0 m per floor
            total_height = 3.0 * num_floors

        # 3) The per-floor wall height
        wall_height = total_height / num_floors

    # 1) Assign geometry
    geom_params = assign_geometry_values(
        building_row=building_row,
        calibration_stage=calibration_stage,
        strategy=strategy,
        random_seed=random_seed,
        user_config=user_config,
        assigned_geom_log=assigned_geom_log,
        excel_rules=excel_rules  # optional
    )
    perimeter_depth = geom_params["perimeter_depth"]
    has_core = geom_params["has_core"]

    # 2) floors
    num_floors = building_row.get("gem_bouwlagen", 1)

    # 3) dimensions
    width, length = compute_dimensions_from_area_perimeter(area, perimeter)

    # 4) base polygon
    A0, B0, C0, D0 = create_building_base_polygon(width, length, orientation)
    base_poly_0 = [A0, B0, C0, D0]

    # 5) zones per floor
    floors_zones = {}
    current_base_poly = base_poly_0
    for floor_i in range(1, num_floors + 1):
        floor_type = "Ground" if floor_i == 1 else "Internal"
        is_top_floor = (floor_i == num_floors)

        zones_data = create_zones_with_perimeter_depth(
            idf=idf,
            floor_i=floor_i,
            base_poly=current_base_poly,
            wall_height=wall_height,
            edge_types=edge_types,
            perimeter_depth=perimeter_depth,
            floor_type=floor_type,
            has_core=has_core,
            is_top_floor=is_top_floor
        )
        current_base_poly = [(p[0], p[1], p[2] + wall_height) for p in current_base_poly]
        floors_zones[floor_i] = zones_data

    # If you want to add roof slope logic, do it here

    return floors_zones
