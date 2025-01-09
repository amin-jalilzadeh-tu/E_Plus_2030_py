# Elec\overrides_helper.py

def find_applicable_overrides(building_id, building_type, age_range, user_config):
    matches = []
    for row in user_config:
        # building_id check
        if "building_id" in row and row["building_id"] != building_id:
            continue
        # building_type check
        if "building_type" in row and row["building_type"] != building_type:
            continue
        # age_range check
        if "age_range" in row and row["age_range"] != age_range:
            continue
        matches.append(row)
    return matches



# incorporate a user_config table that can override default lighting parameters for:

# A specific building ID
# A building type (e.g. "Office", "residential")
# A combo of building type + age range (“archetype”)