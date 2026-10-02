"""Price checks using the actual MRP entered for this product; no mock market data."""


def assess_price(mrp, dealer_price):
    if mrp is None or dealer_price is None:
        return "missing", "Enter both the printed MRP and dealer quote to compare them. Recent local input prices are not connected."
    if dealer_price > mrp:
        return "above_mrp", "The dealer quote is above the MRP you entered. Recheck the printed pack price and ask the dealer to explain the difference."
    return "at_or_below_mrp", "The dealer quote is at or below the MRP you entered. Confirm the printed MRP and any applicable charges before paying."
