# Example dictionary with schedule definitions
# Each sub-type has "weekday" and "weekend" lists of (start_hour, end_hour, fraction).
SCHEDULE_DEFINITIONS = {
    "Residential": {
        # -------------------------------------------------
        # All sub-types could share a similar schedule,
        # or be individually detailed. We'll show one example.
        # -------------------------------------------------
        "Corner House": {
            "weekday": [
                (0, 6, 0.05),
                (6, 8, 0.30),
                (8, 17, 0.10),
                (17, 22, 0.50),
                (22, 24, 0.05),
            ],
            "weekend": [
                (0, 8, 0.10),
                (8, 22, 0.40),
                (22, 24, 0.10),
            ],
        },
        "Apartment": {
            "weekday": [
                (0, 6, 0.05),
                (6, 8, 0.20),
                (8, 18, 0.10),
                (18, 23, 0.60),
                (23, 24, 0.05),
            ],
            "weekend": [
                (0, 9, 0.15),
                (9, 22, 0.50),
                (22, 24, 0.15),
            ],
        },
        "Terrace or Semi-detached House": {
            "weekday": [
                (0, 7, 0.05),
                (7, 9, 0.20),
                (9, 17, 0.10),
                (17, 22, 0.60),
                (22, 24, 0.05),
            ],
            "weekend": [
                (0, 9, 0.10),
                (9, 22, 0.50),
                (22, 24, 0.10),
            ],
        },
        "Detached House": {
            "weekday": [
                (0, 7, 0.05),
                (7, 9, 0.20),
                (9, 17, 0.10),
                (17, 22, 0.60),
                (22, 24, 0.05),
            ],
            "weekend": [
                (0, 9, 0.10),
                (9, 22, 0.50),
                (22, 24, 0.10),
            ],
        },
        "Two-and-a-half-story House": {
            "weekday": [
                (0, 6, 0.05),
                (6, 9, 0.20),
                (9, 18, 0.10),
                (18, 23, 0.60),
                (23, 24, 0.05),
            ],
            "weekend": [
                (0, 9, 0.10),
                (9, 22, 0.50),
                (22, 24, 0.10),
            ],
        },
    },
    "Non-Residential": {
        "Meeting Function": {
            "weekday": [
                (0, 6, 0.05),
                (6, 9, 0.50),
                (9, 12, 0.80),
                (12, 13, 0.50),
                (13, 18, 0.80),
                (18, 20, 0.50),
                (20, 24, 0.10),
            ],
            "weekend": [
                (0, 24, 0.10),
            ],
        },
        "Healthcare Function": {
            "weekday": [
                (0, 24, 0.80),  # Healthcare often 24/7
            ],
            "weekend": [
                (0, 24, 0.80),
            ],
        },
        "Sport Function": {
            "weekday": [
                (0, 6, 0.05),
                (6, 9, 0.20),
                (9, 12, 0.70),
                (12, 14, 0.50),
                (14, 22, 0.70),
                (22, 24, 0.10),
            ],
            "weekend": [
                (0, 9, 0.10),
                (9, 22, 0.70),
                (22, 24, 0.10),
            ],
        },
        "Cell Function": {
            # Example, cell function might be more continuous
            "weekday": [
                (0, 24, 0.90),
            ],
            "weekend": [
                (0, 24, 0.90),
            ],
        },
        "Retail Function": {
            "weekday": [
                (0, 6, 0.05),
                (6, 9, 0.30),
                (9, 19, 0.90),
                (19, 21, 0.50),
                (21, 24, 0.05),
            ],
            "weekend": [
                (0, 8, 0.10),
                (8, 19, 0.80),
                (19, 22, 0.30),
                (22, 24, 0.10),
            ],
        },
        "Industrial Function": {
            "weekday": [
                (0, 6, 0.20),
                (6, 8, 0.50),
                (8, 17, 0.80),
                (17, 20, 0.50),
                (20, 24, 0.20),
            ],
            "weekend": [
                (0, 24, 0.20),
            ],
        },
        "Accommodation Function": {
            "weekday": [
                (0, 24, 0.70),
            ],
            "weekend": [
                (0, 24, 0.70),
            ],
        },
        "Office Function": {
            # As given in the example
            "weekday": [
                (0, 6, 0.10),
                (6, 9, 0.50),
                (9, 12, 0.90),
                (12, 13, 0.70),
                (13, 18, 0.90),
                (18, 20, 0.50),
                (20, 24, 0.10),
            ],
            "weekend": [
                (0, 24, 0.10),
            ],
        },
        "Education Function": {
            "weekday": [
                (0, 7, 0.05),
                (7, 8, 0.50),
                (8, 16, 0.80),
                (16, 18, 0.50),
                (18, 24, 0.05),
            ],
            "weekend": [
                (0, 24, 0.10),
            ],
        },
        "Other Use Function": {
            "weekday": [
                (0, 24, 0.30),
            ],
            "weekend": [
                (0, 24, 0.20),
            ],
        },
    },
}
