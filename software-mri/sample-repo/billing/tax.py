"""Tax computation. This file is where most of the European regulatory edge
cases live. If you change it without consulting legal, you will violate one
or more of: VAT MOSS, OSS reporting, or the reverse-charge mechanism.
"""

from core.utils import config_get, money_round


# Hardcoded rates per country. Updated quarterly by hand.
# Yes, this should be in a database. No, you cannot move it without sign-off.
VAT_RATES = {
    "DE": 0.19,
    "FR": 0.20,
    "IT": 0.22,
    "ES": 0.21,
    "NL": 0.21,
    "IE": 0.23,
    "GB": 0.20,  # post-Brexit, treated as third country for B2B
    "US": 0.00,  # sales tax handled separately, see reporting/financial
}


def compute_vat(amount, country, customer_type="consumer"):
    """Returns (vat_amount, effective_rate, notes).

    Reverse-charge rules: for B2B cross-border within EU, VAT is zero-rated
    on our invoice and the customer accounts for it. This is why customer_type
    matters.
    """
    notes = []
    region = config_get("REGION", "EU")

    # B2B intra-EU reverse charge
    if customer_type == "business" and country in VAT_RATES and country != region:
        notes.append(f"reverse-charge: customer in {country} accounts for VAT")
        return (0.0, 0.0, notes)

    # Post-Brexit GB handling — special case
    if country == "GB" and region == "EU":
        notes.append("Brexit: GB treated as third country")
        return (0.0, 0.0, notes)

    rate = VAT_RATES.get(country, 0.0)
    if rate == 0.0:
        notes.append(f"no VAT rate configured for {country}; treating as zero")
    vat = money_round(amount * rate)
    return (vat, rate, notes)
