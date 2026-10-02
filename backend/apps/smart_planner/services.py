"""Pure planning calculations. No database or HTTP concerns belong here."""
import html
import math
from .rules import COCONUT_RULES, IRRIGATION_RULES, INTERCROP_RULES, COSTS


def validate_boundary(boundary):
    if not isinstance(boundary, list) or len(boundary) < 3 or len(boundary) > 100:
        raise ValueError("A plot needs between 3 and 100 boundary points.")
    points = []
    for point in boundary:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError("Each boundary point needs an x and y value.")
        x, y = float(point[0]), float(point[1])
        if not math.isfinite(x) or not math.isfinite(y) or abs(x) > 100000 or abs(y) > 100000:
            raise ValueError("Boundary coordinates are outside the supported range.")
        points.append([x, y])
    if polygon_area(points) <= 25:
        raise ValueError("The selected area is too small for this planning tool.")
    return points


def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points))) / 2)


def geojson_to_local(geojson):
    """Project a small WGS84 polygon into local metres for spacing calculations."""
    if not isinstance(geojson, dict) or geojson.get("type") != "Polygon":
        raise ValueError("A GeoJSON Polygon is required.")
    rings = geojson.get("coordinates")
    if not isinstance(rings, list) or not rings or len(rings[0]) < 4:
        raise ValueError("A polygon needs at least three points and a closing point.")
    raw = rings[0][:-1] if rings[0][0] == rings[0][-1] else rings[0]
    if len(raw) < 3 or len(raw) > 100:
        raise ValueError("A plot needs between 3 and 100 boundary points.")
    lon0 = sum(float(p[0]) for p in raw) / len(raw)
    lat0 = sum(float(p[1]) for p in raw) / len(raw)
    earth = 111320.0
    local = [[(float(lon) - lon0) * earth * math.cos(math.radians(lat0)), (float(lat) - lat0) * earth] for lon, lat in raw]
    return validate_boundary(local), {"lat": lat0, "lon": lon0}, {"type": "Polygon", "coordinates": [[list(map(float, p)) for p in raw + [raw[0]]]]}


def analyse_geojson(geojson):
    local, center, normalized = geojson_to_local(geojson)
    result = analyse_plot(local)
    result.update({"boundary_geojson": normalized, "center_lat": round(center["lat"], 7), "center_lon": round(center["lon"], 7), "coordinate_system": "WGS84"})
    return result


def _distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def analyse_plot(boundary):
    points = validate_boundary(boundary)
    area = polygon_area(points)
    xs, ys = zip(*points)
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    ratio = max(width, height) / max(min(width, height), 0.01)
    perimeter = sum(_distance(points[i], points[(i + 1) % len(points)]) for i in range(len(points)))
    if ratio > 3.0: shape = "Long and narrow"
    elif len(points) == 3: shape = "Triangular / wedge-like"
    elif abs(width - height) / max(width, height, 0.01) < 0.18: shape = "Square-like"
    elif ratio < 1.8: shape = "Rectangular"
    else: shape = "Irregular"
    return {"boundary": points, "area_sq_m": round(area, 1), "area_acres": round(area / 4046.8564224, 3),
            "area_cents": round(area / 40.468564224, 1), "area_hectares": round(area / 10000, 4),
            "shape_type": shape, "perimeter_m": round(perimeter, 1), "usable_area_sq_m": round(area * 0.93, 1)}


def _inside(point, polygon):
    x, y = point; inside = False
    for i in range(len(polygon)):
        x1, y1 = polygon[i]; x2, y2 = polygon[(i + 1) % len(polygon)]
        if ((y1 > y) != (y2 > y)) and x < (x2 - x1) * (y - y1) / (y2 - y1 or 1e-9) + x1: inside = not inside
    return inside


def _bounds(points):
    xs, ys = zip(*points); return min(xs), min(ys), max(xs), max(ys)


def coconut_layout(boundary, usable_area):
    points = validate_boundary(boundary)
    min_x, min_y, max_x, max_y = _bounds(points)
    buffer = COCONUT_RULES["boundary_buffer_m"]
    left, bottom, right, top = min_x + buffer, min_y + buffer, max_x - buffer, max_y - buffer
    candidates=[]; x=left
    while x <= right and len(candidates) < 1000:
        y=bottom
        while y <= top and len(candidates) < 1000:
            if _inside([x,y], points): candidates.append([round(x,2),round(y,2)])
            y += COCONUT_RULES["spacing_y_m"]
        x += COCONUT_RULES["spacing_x_m"]
    width = max(right-left, 0); rows = max(1, math.floor(width / COCONUT_RULES["spacing_x_m"])+1)
    plants_per_row = max(1, math.ceil(len(candidates) / rows)) if candidates else 0
    return {"spacing_x_m": COCONUT_RULES["spacing_x_m"], "spacing_y_m": COCONUT_RULES["spacing_y_m"],
            "boundary_buffer_m": buffer, "estimated_tree_count": len(candidates), "layout_points": candidates,
            "row_count": rows if candidates else 0, "plants_per_row_estimate": plants_per_row,
            "rule_note": "Standard planning reference; verify locally for variety, slope, soil and field access."}


def irrigation_plan(plot, layout, water_source, budget, preference, requested_method=None):
    source = water_source.lower(); budget = budget.lower()
    if requested_method == "sprinkler":
        method, reason = "Sprinkler irrigation", "Sprinklers can cover wider zones; verify pressure and wind exposure locally."
    elif source == "rainfed" or source in ("other", "not sure"):
        method, reason = "Water source verification required", IRRIGATION_RULES["rainfed"]
    elif budget == "low" or preference == "low-cost":
        method, reason = "Phased basin → drip", IRRIGATION_RULES["low_cost"]
    else:
        method, reason = "Drip irrigation", IRRIGATION_RULES["drip"]
    tree_count = layout["estimated_tree_count"]
    rows = layout["row_count"]
    span = max(math.sqrt(plot["usable_area_sq_m"]), 10)
    main = round(max(span * 0.7, 18), 1); sub = round(max(rows * 7.5, 12), 1); lateral = round(tree_count * 3.1, 1)
    drippers = tree_count * 2 if "drip" in method.lower() else 0
    sprinklers = max(1, math.ceil(tree_count / 16)) if "sprinkler" in method.lower() else 0
    return {"recommended_method": method, "reason": reason, "main_pipe_length_m": main, "sub_main_length_m": sub,
            "lateral_length_m": lateral, "dripper_count": drippers, "sprinkler_count": sprinklers,
            "filter_required": method.startswith("Drip"), "valves_required": max(1, rows // 4) if rows else 1,
            "layout": {"water_source": [5, 8], "main_line": [[5,8],[20,8]], "rows": rows,
                       "tree_points": layout["layout_points"]}}


def intercrops(age, water_source, soil):
    key = age if age in INTERCROP_RULES else "new"
    return [{"crop_name": name, "suitability_level": "Possible option", "reason": reason,
             "water_requirement": water, "labour_requirement": labour,
             "season_note": "Confirm local season and market before planting.", "income_note": "Possible extra-income option; no income is guaranteed."}
            for name, reason, water, labour in INTERCROP_RULES[key]]


def material_estimate(irrigation, budget):
    items = [
        ("Main pipe", irrigation["main_pipe_length_m"], "m", "main_pipe_m"),
        ("Sub-main pipe", irrigation["sub_main_length_m"], "m", "sub_main_m"),
        ("Lateral pipe", irrigation["lateral_length_m"], "m", "lateral_m"),
        ("Root-zone drippers", irrigation["dripper_count"], "nos", "dripper"),
        ("Filter", 1 if irrigation["filter_required"] else 0, "nos", "filter"),
        ("Control valve", irrigation["valves_required"], "nos", "valve"),
        ("Fittings / end caps", 1, "set", "fitting_set"),
        ("Installation labour", 1, "set", "labour"),
    ]
    return [{"item_name": n, "quantity": round(q,1), "unit": u, "estimated_low_cost": round(q*COSTS[k][0]),
             "estimated_high_cost": round(q*COSTS[k][1]), "notes": "Rough planning range"} for n,q,u,k in items if q > 0]


def render_layout_svg(plot, irrigation, layout):
    pts = layout["layout_points"] or []
    bx, by, max_x, max_y = _bounds(plot["boundary"]); min_x = bx; scale=4; ox, oy=20, 170
    boundary = " ".join(f"{ox+(x-bx)*scale:.1f},{oy-(y-by)*scale:.1f}" for x,y in plot["boundary"])
    circles = "".join(f'<circle cx="{ox+(x-bx)*scale:.1f}" cy="{oy-(y-by)*scale:.1f}" r="3"/>' for x,y in pts)
    source=irrigation["layout"]["water_source"]; main=irrigation["layout"]["main_line"]
    line=f'<path d="M {ox+source[0]*scale} {oy-source[1]*scale} L {ox+(main[1][0])*scale} {oy-(main[1][1])*scale}" class="main"/>'
    laterals = "".join(f'<path d="M {ox+(min(x for x,_ in pts)-bx)*scale:.1f} {oy-(y-by)*scale:.1f} L {ox+(max(x for x,_ in pts)-bx)*scale:.1f} {oy-(y-by)*scale:.1f}" class="lateral"/>' for y in sorted(set(y for _, y in pts))) if pts else ""
    drippers = "".join(f'<circle cx="{ox+(x-bx)*scale:.1f}" cy="{oy-(y-by)*scale:.1f}" r="1.3" class="dripper"/>' for x,y in pts) if irrigation.get("dripper_count") else ""
    sprinkler_count = irrigation.get("sprinkler_count", 0)
    sprinklers = "".join(f'<circle cx="{ox+(x-bx)*scale:.1f}" cy="{oy-(y-by)*scale:.1f}" r="18" class="coverage"/><circle cx="{ox+(x-bx)*scale:.1f}" cy="{oy-(y-by)*scale:.1f}" r="3" class="sprinkler"/>' for x,y in pts[::max(1, len(pts)//max(1, sprinkler_count))][:sprinkler_count])
    intercrop = f'<rect x="{ox+8}" y="{oy-105}" width="{max(50, (max_x-min_x)*scale-16):.1f}" height="22" class="intercrop"/><text x="{ox+12}" y="{oy-91}">Suggested intercrop zone</text>' if pts else ""
    return f'''<svg viewBox="0 0 520 230" role="img" aria-label="Preliminary coconut and irrigation layout" xmlns="http://www.w3.org/2000/svg"><rect width="520" height="230" fill="#f6f7ef"/><polygon points="{boundary}" class="boundary"/>{intercrop}<g class="trees">{circles}</g>{laterals}{drippers}{sprinklers}{line}<circle cx="{ox+source[0]*scale}" cy="{oy-source[1]*scale}" r="8" class="source"/><text x="20" y="220">Water source</text><text x="150" y="25">Trees, pipes and irrigation zones · {len(pts)} trees</text><style>.boundary{{fill:#e5eed8;stroke:#58794e;stroke-width:2;stroke-dasharray:6 4}}.trees{{fill:#6d8d55}}.main{{stroke:#a66f3c;stroke-width:3}}.lateral{{stroke:#7193a0;stroke-width:1.3;stroke-dasharray:4 3}}.dripper{{fill:#3e7888}}.sprinkler{{fill:#3e7888}}.coverage{{fill:#8db6c044;stroke:#6a99a3;stroke-width:1;stroke-dasharray:3 2}}.source{{fill:#5b8cac;stroke:white;stroke-width:3}}.intercrop{{fill:#d7c88655;stroke:#b69b4c;stroke-width:1}}text{{font:11px sans-serif;fill:#52634d}}</style></svg>'''


def generate_plan(analysis, inputs):
    layout = coconut_layout(analysis["boundary"], analysis["usable_area_sq_m"])
    irrigation = irrigation_plan(analysis, layout, inputs["water_source"], inputs["budget_level"], inputs["irrigation_preference"], inputs.get("requested_method"))
    intercrop = intercrops(inputs["coconut_age"], inputs["water_source"], inputs["soil_type"])
    materials = material_estimate(irrigation, inputs["budget_level"])
    total_low, total_high = sum(i["estimated_low_cost"] for i in materials), sum(i["estimated_high_cost"] for i in materials)
    return {"plot": analysis, "coconut_layout": layout, "irrigation": irrigation, "intercrops": intercrop,
            "materials": materials, "cost": {"low": total_low, "high": total_high},
            "next_action": "Request officer review before purchasing materials.",
            "disclaimer": "Preliminary planning estimate. Field verification is recommended before planting or installation.",
            "layout_svg": render_layout_svg(analysis, irrigation, layout)}
