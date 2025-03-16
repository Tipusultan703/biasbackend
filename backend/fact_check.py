import requests

FACT_CHECK_APIS = [
    "https://factchecktools.googleapis.com/v1alpha1/claims:search",
    "https://api.politifact.com/v2/claims"
]

def verify_fact(statement):
    results = []
    for api_url in FACT_CHECK_APIS:
        try:
            response = requests.get(api_url, params={"query": statement})
            if response.status_code == 200:
                fact_check_data = response.json()
                results.append(fact_check_data)
        except Exception as e:
            print(f"Error fetching fact check data: {e}")

    return results if results else ["No direct fact-check found."]

from forex_python.converter import CurrencyRates

c = CurrencyRates()
inflation_rate = 3.2  # Assume 3.2% yearly inflation

def adjust_for_inflation(amount, year):
    years_passed = 2025 - year
    adjusted_value = amount * ((1 + (inflation_rate / 100)) ** years_passed)
    return round(adjusted_value, 2)

