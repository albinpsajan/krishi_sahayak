"""Editable agronomy and cost references. These are planning defaults, not quotes."""
COCONUT_RULES = {
    "spacing_x_m": 7.5, "spacing_y_m": 7.5, "boundary_buffer_m": 2.0,
    "recommended_system": "square",
}
IRRIGATION_RULES = {
    "drip_sources": {"well", "borewell", "pond", "canal"},
    "low_cost": "Basin irrigation now, with a drip upgrade when budget allows.",
    "drip": "Drip irrigation targets each tree’s root zone, saves water, and can support future fertigation.",
    "rainfed": "Water source verification is required. Consider rainwater harvesting before final pipe design.",
}
INTERCROP_RULES = {
    "new": [("Banana", "Earlier income while coconut is growing.", "Medium to high", "Medium"),
            ("Pineapple", "Uses open space between young coconut rows.", "Medium", "Medium"),
            ("Turmeric", "Short-duration seasonal option in filtered light.", "Medium", "Medium")],
    "1–3 years": [("Banana", "Can use open inter-row space while the canopy is developing.", "Medium to high", "Medium"),
                  ("Ginger", "Short-duration crop option where drainage is good.", "Medium", "Medium")],
    "4–7 years": [("Pepper", "Can use suitable support trees after local field verification.", "Medium", "High"),
                  ("Cocoa", "May suit partially shaded systems with enough moisture.", "Medium", "Medium")],
    "mature": [("Pepper", "Possible under a suitable, ventilated coconut canopy.", "Medium", "High"),
                ("Fodder grass", "Useful where livestock or fodder demand exists.", "Medium", "Medium"),
                ("Elephant foot yam", "Seasonal option where soil and shade are suitable.", "Medium", "Medium")],
}
COSTS = {
    "main_pipe_m": (45, 75), "sub_main_m": (22, 42), "lateral_m": (7, 12),
    "dripper": (8, 20), "filter": (1800, 4200), "valve": (250, 700), "fitting_set": (1800, 4200), "labour": (3500, 8500),
}
