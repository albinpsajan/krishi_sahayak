from apps.smart_planner.services import generate_plan

def apply_change(plan, plot, change_type, note):
    inputs = {"water_source": plan.water_source, "budget_level": plan.budget_level, "irrigation_preference": plan.irrigation_preference, "coconut_age": plan.coconut_age, "soil_type": plan.soil_type, "requested_method": None}
    text = (note or "").lower()
    if change_type == "Change irrigation method":
        inputs["requested_method"] = "sprinkler" if "sprinkler" in text else "drip"
    elif change_type == "Reduce cost": inputs["budget_level"] = "low"
    elif change_type == "Change crop spacing":
        inputs["irrigation_preference"] = "long-term" if "increase" in text or "wide" in text else plan.irrigation_preference
    elif change_type == "Add/remove intercrop":
        inputs["coconut_age"] = "new" if "remove" in text else plan.coconut_age
    if "water-saving" in text: inputs["irrigation_preference"] = "water-saving"
    if "low budget" in text or "low-cost" in text: inputs["budget_level"] = "low"
    return generate_plan(plot, inputs)
