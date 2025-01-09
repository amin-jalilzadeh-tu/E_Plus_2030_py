# Elec/lighting_lookup.py
"""
Lighting Lookup Table (Pre/Post Calibration)
---------------------------------------------
This file implements default lighting parameters for both residential and non-residential
functions, consistent with NTA 8800 methodology. These parameters are used when actual
lighting installations or measured data are unavailable.

Relevant NTA 8800 references:
  - Residential lighting = 0 kWh/m² (NTA 8800 §14.2.1)
  - Non-residential tD/tN (burning hours): Table 14.1
  - Default W/m² for unknown lighting: Table 14.3
  - Default parasitic power => ~0.285 W/m² derived from 2.5 kWh/m²/year (NTA 8800 §14.3.3 & 14.3.4)
"""

lighting_lookup = {
    "pre_calibration": {
        # ===============================
        # 1) RESIDENTIAL (all sub-types)
        # ===============================
        # Per NTA 8800 §14.2.1:
        #   - WL;spec = 0 kWh/m²
        #   - WP = 0  => no parasitic
        "Residential": {
            "Corner House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),   # no daytime burning hours
                "tN_range": (0, 0)    # no nighttime burning hours
            },
            "Apartment": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Terrace or Semi-detached House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Detached House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Two-and-a-half-story House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            }
        },

        # ===============================
        # 2) NON-RESIDENTIAL
        # ===============================
        # For non-residential, we use lumpsum W/m² based on table 14.3
        # and typical tD/tN from table 14.1. Parasitic ~0.28..0.30 W/m².
        "Non-Residential": {
            "Meeting Function": {
                # Example: from NTA 8800 table 14.1 => tD=2200, tN=300
                # Default lumpsum W/m² ~ 16-18 for typical meeting spaces
                "LIGHTS_WM2_range": (16.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (2100, 2300),
                "tN_range": (300, 400)
            },
            "Healthcare Function": {
                # Healthcare can be ~17-19 W/m² lumpsum (or 15-20 depending on details)
                # Two major subcases in table 14.1:
                #   - With bed area => tD=4000, tN=1000
                #   - Other => tD=2200, tN=300
                # Here we pick slightly broader ranges to cover both.
                "LIGHTS_WM2_range": (17.0, 19.0),
                "PARASITIC_WM2_range": (0.28, 0.31),
                "tD_range": (2100, 4200),
                "tN_range": (300, 1100)
            },
            "Sport Function": {
                # Per table 14.1 => tD=2200, tN=800
                "LIGHTS_WM2_range": (16.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (2100, 2300),  # or (2200, 2200) if you want a single value
                "tN_range": (700, 900)
            },
            "Cell Function": {
                # Per table 14.1 => tD=4000, tN=1000
                "LIGHTS_WM2_range": (16.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (3800, 4200),
                "tN_range": (900, 1100)
            },
            "Retail Function": {
                # Table 14.1 => tD=2700, tN=400
                # Table 14.3 => 30 W/m² for shops as lumpsum
                "LIGHTS_WM2_range": (29.0, 31.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (2600, 2800),
                "tN_range": (300, 500)
            },
            "Industrial Function": {
                # Not explicitly in table 14.1, so often treated similarly to 'Other'
                # Suppose typical tD=2200, tN=300
                "LIGHTS_WM2_range": (16.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (2100, 2300),
                "tN_range": (300, 400)
            },
            "Accommodation Function": {
                # Table 14.1 => tD=4000, tN=1000
                "LIGHTS_WM2_range": (16.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (3800, 4200),
                "tN_range": (900, 1100)
            },
            "Office Function": {
                # Table 14.1 => tD=2200, tN=300
                # Table 14.3 => ~15–17 W/m² lumpsum for offices
                "LIGHTS_WM2_range": (15.0, 17.0),
                "PARASITIC_WM2_range": (0.28, 0.29),
                "tD_range": (2100, 2300),
                "tN_range": (300, 400)
            },
            "Education Function": {
                # Table 14.1 => tD=1600, tN=300
                "LIGHTS_WM2_range": (13.0, 16.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (1500, 1700),
                "tN_range": (200, 400)
            },
            "Other Use Function": {
                # Fallback for any non-res type not covered above
                "LIGHTS_WM2_range": (15.0, 18.0),
                "PARASITIC_WM2_range": (0.28, 0.30),
                "tD_range": (2000, 2500),
                "tN_range": (200, 500)
            }
        }
    },

    # ----------------------------------------------------------------
    # Post-calibration stage: fixed or narrower ranges (example only)
    # Typically, these values get “locked in” after measurement-based
    # or finalized calibration. Adjust as needed for your project.
    # ----------------------------------------------------------------
    "post_calibration": {
        "Residential": {
            "Corner House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Apartment": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Terrace or Semi-detached House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Detached House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            },
            "Two-and-a-half-story House": {
                "LIGHTS_WM2_range": (0.0, 0.0),
                "PARASITIC_WM2_range": (0.0, 0.0),
                "tD_range": (0, 0),
                "tN_range": (0, 0)
            }
        },
        "Non-Residential": {
            "Meeting Function": {
                # Narrow or locked after calibration
                "LIGHTS_WM2_range": (17.0, 17.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2200, 2200),
                "tN_range": (300, 300)
            },
            "Healthcare Function": {
                "LIGHTS_WM2_range": (18.0, 18.0),
                "PARASITIC_WM2_range": (0.29, 0.29),
                "tD_range": (4000, 4000),
                "tN_range": (1000, 1000)
            },
            "Sport Function": {
                "LIGHTS_WM2_range": (17.0, 17.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2200, 2200),
                "tN_range": (800, 800)
            },
            "Cell Function": {
                "LIGHTS_WM2_range": (17.0, 17.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (4000, 4000),
                "tN_range": (1000, 1000)
            },
            "Retail Function": {
                "LIGHTS_WM2_range": (30.0, 30.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2700, 2700),
                "tN_range": (400, 400)
            },
            "Industrial Function": {
                "LIGHTS_WM2_range": (17.0, 17.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2200, 2200),
                "tN_range": (300, 300)
            },
            "Accommodation Function": {
                "LIGHTS_WM2_range": (17.0, 17.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (4000, 4000),
                "tN_range": (1000, 1000)
            },
            "Office Function": {
                "LIGHTS_WM2_range": (16.0, 16.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2200, 2200),
                "tN_range": (300, 300)
            },
            "Education Function": {
                "LIGHTS_WM2_range": (15.0, 15.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (1600, 1600),
                "tN_range": (300, 300)
            },
            "Other Use Function": {
                "LIGHTS_WM2_range": (16.0, 16.0),
                "PARASITIC_WM2_range": (0.285, 0.285),
                "tD_range": (2200, 2200),
                "tN_range": (300, 300)
            }
        }
    }
}
