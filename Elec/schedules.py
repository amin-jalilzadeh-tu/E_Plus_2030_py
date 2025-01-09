# Elec/schedules.py
from .schedule_def import SCHEDULE_DEFINITIONS
"""
This module creates detailed lighting schedules for weekdays and weekends,
differentiating by building function (Residential vs. Non-Residential)
and by sub-type.

The dictionary 'SCHEDULE_DEFINITIONS' holds typical hourly fractions
for each sub-type. For instance, an "Office Function" might have higher lighting usage
during normal working hours on weekdays, and minimal usage on weekends.

We then have two main functions:
1) create_lighting_schedule(idf, building_category, sub_type, schedule_name)
   - Creates a multi-day schedule with 'WeekDays', 'Saturday', 'Sunday' definitions.

2) create_parasitic_schedule(idf, sched_name)
   - Creates an always-on (1.0) schedule for parasitic loads (24/7).

IMPORTANT NOTES:
- The example fraction patterns are placeholders and can be refined as needed.
- Some sub-types (especially Residential) may have simpler or more complex usage patterns.
- You can adapt to do "For: AllDays" if you do NOT want separate weekend logic.
"""



def create_lighting_schedule(idf, building_category, sub_type, schedule_name="LightsSchedule"):
    """
    Create a SCHEDULE:COMPACT in the IDF with different time blocks for
    WeekDays (Mon-Fri), Saturday, and Sunday based on building_category + sub_type.

    building_category: "Residential" or "Non-Residential"
    sub_type: e.g. "Corner House", "Office Function", etc.
    schedule_name: name of schedule in IDF

    The function looks up SCHEDULE_DEFINITIONS and writes out fractional
    lighting levels for each hour-block.

    Returns the schedule object name in IDF.
    """

    # Attempt to get sub-type dictionary
    try:
        sub_dict = SCHEDULE_DEFINITIONS[building_category][sub_type]
    except KeyError:
        # Fallback: If no match, create a simple always-0.5 schedule
        sub_dict = {
            "weekday": [(0, 24, 0.5)],
            "weekend": [(0, 24, 0.5)],
        }

    # Create the schedule object
    schedule = idf.newidfobject("SCHEDULE:COMPACT")
    schedule.Name = schedule_name
    schedule.Schedule_Type_Limits_Name = "Fraction"

    # We define three sets of fields in a row:
    #   1) For: WeekDays
    #   2) For: Saturday
    #   3) For: Sunday
    #
    # The pattern is:
    #   Field_1 = "Through: 12/31"  (end of year)
    #   Field_2 = "For: Weekdays"
    #   Field_3 = "Until: HH:MM,<fraction>"
    #   ...
    # Then another "For: Saturday" set, etc.

    # Field index pointer as we fill them
    field_idx = 1

    # Always start with:
    setattr(schedule, f"Field_{field_idx}", "Through: 12/31")
    field_idx += 1

    # 1) WEEKDAYS
    setattr(schedule, f"Field_{field_idx}", "For: WeekDays")
    field_idx += 1
    for (start_hour, end_hour, frac) in sub_dict["weekday"]:
        setattr(schedule, f"Field_{field_idx}",
                f"Until: {end_hour:02d}:00,{frac:.2f}")
        field_idx += 1

    # 2) SATURDAY
    setattr(schedule, f"Field_{field_idx}", "For: Saturday")
    field_idx += 1
    for (start_hour, end_hour, frac) in sub_dict["weekend"]:
        setattr(schedule, f"Field_{field_idx}",
                f"Until: {end_hour:02d}:00,{frac:.2f}")
        field_idx += 1

    # 3) SUNDAY
    setattr(schedule, f"Field_{field_idx}", "For: Sunday")
    field_idx += 1
    for (start_hour, end_hour, frac) in sub_dict["weekend"]:
        setattr(schedule, f"Field_{field_idx}",
                f"Until: {end_hour:02d}:00,{frac:.2f}")
        field_idx += 1

    return schedule.Name


def create_parasitic_schedule(idf, sched_name="LightsParasiticSchedule"):
    """
    Creates a schedule that is always on at 1.0 (24/7).
    """
    schedule = idf.newidfobject("SCHEDULE:COMPACT")
    schedule.Name = sched_name
    schedule.Schedule_Type_Limits_Name = "Fraction"

    # Simple approach: same every day
    schedule.Field_1 = "Through: 12/31"
    schedule.Field_2 = "For: AllDays"
    schedule.Field_3 = "Until: 24:00,1.0"

    return schedule.Name
