"""Quantity planning only when the farmer supplies a rate copied from the label."""


def estimate_quantity(area_acres, label_rate_per_acre, label_rate_unit, purchase_quantity, purchase_unit):
    if label_rate_per_acre is None:
        return None, "", "No estimate shown. Enter a per-acre rate from the product label; do not use an unverified app dosage."
    estimate = round(area_acres * label_rate_per_acre, 2)
    unit = label_rate_unit or "kg"
    if purchase_quantity is None:
        note = "Planning amount uses the per-acre rate you entered from the label. Confirm the label and officer guidance before application."
    elif (purchase_unit or unit).casefold() != unit.casefold():
        note = "The entered purchase unit differs from the label-rate unit, so an overbuy check is unavailable. Confirm units before buying."
    elif purchase_quantity > estimate * 1.25:
        note = "The entered purchase amount is more than 25% above this label-rate estimate. Recheck the area, units, and need before buying."
    else:
        note = "Planning amount uses the per-acre rate you entered from the label. Confirm the label and officer guidance before application."
    return estimate, unit, note
