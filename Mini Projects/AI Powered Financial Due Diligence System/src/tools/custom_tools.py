from crewai.tools import tool

@tool("Risk Calculator Tool")
def calculate_risk_score(scores: str) -> str:
    """
    Calculates the overall risk score from individual risk scores.
    Input should be comma-separated scores like: '7,5,8,6'
    Returns the average risk score and risk level.
    """
    try:
        score_list = [float(s.strip()) for s in scores.split(",")]
        average = sum(score_list) / len(score_list)
        
        if average <= 3:
            level = "LOW RISK"
        elif average <= 6:
            level = "MEDIUM RISK"
        else:
            level = "HIGH RISK"
            
        return f"Overall Risk Score: {average:.1f}/10 — {level}"
    except Exception as e:
        return f"Error calculating risk: {str(e)}"


@tool("Currency Converter Tool")
def convert_currency(amount_and_currencies: str) -> str:
    """
    Converts currency amounts for financial analysis.
    Input format: 'amount FROM_CURRENCY TO_CURRENCY' 
    Example: '1000000 USD INR'
    Uses approximate rates for reference only.
    """
    rates = {
        "USD_INR": 83.5,
        "EUR_INR": 90.2,
        "GBP_INR": 106.0,
        "USD_EUR": 0.92,
        "USD_GBP": 0.79,
        "INR_USD": 0.012,
    }
    
    try:
        parts = amount_and_currencies.strip().split()
        amount = float(parts[0])
        from_curr = parts[1].upper()
        to_curr = parts[2].upper()
        
        key = f"{from_curr}_{to_curr}"
        if key in rates:
            converted = amount * rates[key]
            return f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr} (approximate rate)"
        else:
            return f"Conversion rate for {from_curr} to {to_curr} not available."
    except Exception as e:
        return f"Error converting currency: {str(e)}"