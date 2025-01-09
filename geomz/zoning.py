# D:\Documents\E_Plus_2029_py\geomz\zoning.py

from .geometry import polygon_area, inward_offset_polygon

def link_surfaces(surface_a, surface_b):
    """
    Cross-link two surfaces as interzone partitions:
      1) Both Outside_Boundary_Condition = "Surface"
      2) Each references the other's name
    """
    surface_a.Outside_Boundary_Condition = "Surface"
    surface_b.Outside_Boundary_Condition = "Surface"
    surface_a.Outside_Boundary_Condition_Object = surface_b.Name
    surface_b.Outside_Boundary_Condition_Object = surface_a.Name


def create_zone_surfaces(
    idf,
    zone_name,
    base_poly,
    wall_height,
    floor_bc,
    wall_bcs,
    is_top_floor
):
    """
    Create a rectangular zone (Floor, 4 Walls, and a Roof or Ceiling).

    Parameters
    ----------
    idf : geomeppy.IDF
        The IDF to which we add surfaces.
    zone_name : str
        Name of the new Zone object.
    base_poly : list of (x,y,z)
        4 corner points (in order) for the zone’s base.
    wall_height : float
        Height of the walls.
    floor_bc : str
        BC for the floor (e.g. "Ground", "Adiabatic", "Outdoors", etc.).
    wall_bcs : list of str or dict
        4 items for the wall boundary conditions. If a dict, e.g. {"bc": "Surface", "adj_surf_name": "..."},
        it can store info for cross-linking.
    is_top_floor : bool
        If True => create a roof with Outdoors, else => a ceiling with Adiabatic.

    Returns
    -------
    (zone_name, base_poly, top_poly, created_surfaces)
      zone_name : str
      base_poly : list of points (x,y,z)
      top_poly  : list of points (x,y,z)
      created_surfaces : list of BUILDINGSURFACE:DETAILED created
    """
    zone = idf.newidfobject("ZONE")
    zone.Name = zone_name

    created_surfaces = []

    # ===== Floor =====
    floor_surf = idf.newidfobject("BUILDINGSURFACE:DETAILED")
    floor_surf.Name = f"{zone_name}_Floor"
    floor_surf.Surface_Type = "Floor"
    floor_surf.Zone_Name = zone_name
    floor_surf.Outside_Boundary_Condition = floor_bc

    if floor_bc.lower() == "outdoors":
        floor_surf.Sun_Exposure = "SunExposed"
        floor_surf.Wind_Exposure = "WindExposed"
    else:
        floor_surf.Sun_Exposure = "NoSun"
        floor_surf.Wind_Exposure = "NoWind"

    # Reverse coords so the floor normal faces downward
    floor_surf.setcoords(base_poly[::-1])
    created_surfaces.append(floor_surf)

    # ===== Walls =====
    top_poly = [(p[0], p[1], p[2] + wall_height) for p in base_poly]
    for i in range(4):
        p1 = base_poly[i]
        p2 = base_poly[(i + 1) % 4]
        p1t = top_poly[i]
        p2t = top_poly[(i + 1) % 4]

        wall_coords = [p1, p2, p2t, p1t]
        wall_obj = idf.newidfobject("BUILDINGSURFACE:DETAILED")
        wall_obj.Name = f"{zone_name}_Wall_{i}"
        wall_obj.Surface_Type = "Wall"
        wall_obj.Zone_Name = zone_name

        bc_info = wall_bcs[i]
        if isinstance(bc_info, dict):
            bc_str = bc_info.get("bc", "Adiabatic")
            wall_obj.Outside_Boundary_Condition = bc_str
            if bc_str.lower() == "outdoors":
                wall_obj.Sun_Exposure = "SunExposed"
                wall_obj.Wind_Exposure = "WindExposed"
            else:
                wall_obj.Sun_Exposure = "NoSun"
                wall_obj.Wind_Exposure = "NoWind"

            if bc_str.lower() == "surface":
                # Optionally set the adjacent surface name
                adj_name = bc_info.get("adj_surf_name", "")
                wall_obj.Outside_Boundary_Condition_Object = adj_name
        else:
            # bc_info is just a string
            wall_obj.Outside_Boundary_Condition = bc_info
            if bc_info.lower() == "outdoors":
                wall_obj.Sun_Exposure = "SunExposed"
                wall_obj.Wind_Exposure = "WindExposed"
            else:
                wall_obj.Sun_Exposure = "NoSun"
                wall_obj.Wind_Exposure = "NoWind"

        wall_obj.setcoords(wall_coords)
        created_surfaces.append(wall_obj)

    # ===== Ceiling or Roof =====
    if is_top_floor:
        top_surf = idf.newidfobject("BUILDINGSURFACE:DETAILED")
        top_surf.Name = f"{zone_name}_Roof"
        top_surf.Surface_Type = "Roof"
        top_surf.Zone_Name = zone_name
        top_surf.Outside_Boundary_Condition = "Outdoors"
        top_surf.Sun_Exposure = "SunExposed"
        top_surf.Wind_Exposure = "WindExposed"
        top_surf.setcoords(top_poly)
        created_surfaces.append(top_surf)
    else:
        top_surf = idf.newidfobject("BUILDINGSURFACE:DETAILED")
        top_surf.Name = f"{zone_name}_Ceiling"
        top_surf.Surface_Type = "Ceiling"
        top_surf.Zone_Name = zone_name
        top_surf.Outside_Boundary_Condition = "Adiabatic"
        top_surf.Sun_Exposure = "NoSun"
        top_surf.Wind_Exposure = "NoWind"
        top_surf.setcoords(top_poly)
        created_surfaces.append(top_surf)

    return zone_name, base_poly, top_poly, created_surfaces


def create_zones_with_perimeter_depth(
    idf,
    floor_i,
    base_poly,
    wall_height,
    edge_types,
    perimeter_depth,
    floor_type,
    has_core,
    is_top_floor
):
    """
    Create multiple zones (4 perimeter + 1 core) or a single zone if no core.
    Then explicitly cross-link perimeter-to-core surfaces.

    Returns
    -------
    dict : { zone_name => (base_polygon, top_polygon, list_of_surfaces) }
    """

    def edge_to_bc(e):
        """
        Convert textual edge label to an EnergyPlus BC string:
          - "facade" => "Outdoors"
          - "shared" => "Adiabatic"
          - anything else => "Outdoors"
        """
        low = e.lower().strip()
        if low == "facade":
            return "Outdoors"
        elif low == "shared":
            return "Adiabatic"
        else:
            return "Outdoors"

    zone_data = {}

    # Decide floor boundary
    if floor_type.lower() == "ground":
        floor_bc = "Ground"
    else:
        floor_bc = "Adiabatic"

    # Attempt inward offset for core
    A, B, C, D = base_poly
    inner_poly = None
    if has_core:
        inner_poly = inward_offset_polygon(A, B, C, D, perimeter_depth)
        if inner_poly:
            A2, B2, C2, D2 = inner_poly
            if polygon_area([A2, B2, C2, D2]) < 1e-3:
                inner_poly = None  # not valid

    # Single-zone fallback
    if not inner_poly:
        # No core => just one zone
        wall_bcs = [edge_to_bc(e) for e in edge_types]
        zname, bpoly, tpoly, surf_list = create_zone_surfaces(
            idf,
            f"Zone{floor_i}",
            base_poly,
            wall_height,
            floor_bc,
            wall_bcs,
            is_top_floor
        )
        zone_data[zname] = (bpoly, tpoly, surf_list)
        return zone_data

    # If we do have perimeter+core
    A2, B2, C2, D2 = inner_poly

    # 1) Front perimeter
    front_bc = edge_to_bc(edge_types[0])
    front_base = [A, B, B2, A2]
    # We define the perimeter->core edge as the 3rd wall => "Surface"
    front_walls = [front_bc, "Adiabatic", "Surface", "Adiabatic"]
    zf, fbpoly, ftpoly, fsurfs = create_zone_surfaces(
        idf,
        f"Zone{floor_i}_FrontPerimeter",
        front_base,
        wall_height,
        floor_bc,
        front_walls,
        is_top_floor
    )
    zone_data[zf] = (fbpoly, ftpoly, fsurfs)

    # 2) Right perimeter
    right_bc = edge_to_bc(edge_types[1])
    right_base = [B, C, C2, B2]
    right_walls = [right_bc, "Adiabatic", "Surface", "Adiabatic"]
    zr, rbpoly, rtpoly, rsurfs = create_zone_surfaces(
        idf,
        f"Zone{floor_i}_RightPerimeter",
        right_base,
        wall_height,
        floor_bc,
        right_walls,
        is_top_floor
    )
    zone_data[zr] = (rbpoly, rtpoly, rsurfs)

    # 3) Rear perimeter
    rear_bc = edge_to_bc(edge_types[2])
    rear_base = [C, D, D2, C2]
    rear_walls = [rear_bc, "Adiabatic", "Surface", "Adiabatic"]
    zre, rebpoly, retpoly, resurfs = create_zone_surfaces(
        idf,
        f"Zone{floor_i}_RearPerimeter",
        rear_base,
        wall_height,
        floor_bc,
        rear_walls,
        is_top_floor
    )
    zone_data[zre] = (rebpoly, retpoly, resurfs)

    # 4) Left perimeter
    left_bc = edge_to_bc(edge_types[3])
    left_base = [D, A, A2, D2]
    left_walls = [left_bc, "Adiabatic", "Surface", "Adiabatic"]
    zl, lbpoly, ltpoly, lsurfs = create_zone_surfaces(
        idf,
        f"Zone{floor_i}_LeftPerimeter",
        left_base,
        wall_height,
        floor_bc,
        left_walls,
        is_top_floor
    )
    zone_data[zl] = (lbpoly, ltpoly, lsurfs)

    # 5) Core
    #
    # We pass a reversed polygon so each shared edge is reversed wrt the perimeter side:
    core_poly_reversed = [A2, D2, C2, B2]
    # All edges => "Surface" bc
    core_bc = ["Surface", "Surface", "Surface", "Surface"]
    zc, cbpoly, ctpoly, csurfs = create_zone_surfaces(
        idf,
        f"Zone{floor_i}_Core",
        core_poly_reversed,
        wall_height,
        floor_bc,
        core_bc,
        is_top_floor
    )
    zone_data[zc] = (cbpoly, ctpoly, csurfs)

    # ===================== Cross-Linking =====================
    #
    # We assume:
    #  - The perimeter zone "Wall_2" (index=3 in the surfaces array) is the interior partition
    #  - The matching core zone side is "Wall_x". We'll pick them by index below.
    #
    # Because we reversed the core polygon, each perimeter edge B2->A2 should match an edge A2->B2
    # in the core. We just have to ensure we pick the correct wall indexes. You can adjust as needed.

    # Helper: return the i-th wall object from the created_surfaces list
    # 0=Floor, 1=Wall_0, 2=Wall_1, 3=Wall_2, 4=Wall_3, 5=Roof/Ceiling
    def get_wall(surfs, wall_idx):
        return surfs[1 + wall_idx]  # skip 0=Floor

    # front perimeter interior wall => index=2 => array position=3
    front_interior = get_wall(fsurfs, 2)
    # right perimeter interior => also the 3rd wall => index=2
    right_interior = get_wall(rsurfs, 2)
    # rear perimeter interior => index=2
    rear_interior = get_wall(resurfs, 2)
    # left perimeter interior => index=2
    left_interior = get_wall(lsurfs, 2)

    # In the core zone, we have reversed the polygon. We'll map:
    #   - front perimeter => core wall_3
    #   - right perimeter => core wall_2
    #   - rear perimeter  => core wall_1
    #   - left perimeter  => core wall_0
    #
    # This matches the reversed order of points: [A2->D2->C2->B2].
    # You can confirm or swap if needed.

    core_wall_front = get_wall(csurfs, 3)  # "Wall_3"
    core_wall_right = get_wall(csurfs, 2)  # "Wall_2"
    core_wall_rear  = get_wall(csurfs, 1)  # "Wall_1"
    core_wall_left  = get_wall(csurfs, 0)  # "Wall_0"

    link_surfaces(front_interior, core_wall_front)
    link_surfaces(right_interior, core_wall_right)
    link_surfaces(rear_interior, core_wall_rear)
    link_surfaces(left_interior, core_wall_left)

    return zone_data
