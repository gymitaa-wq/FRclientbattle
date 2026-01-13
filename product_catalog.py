"""
Northwestern Mutual Product Catalog
Comprehensive portfolio of 20+ products for realistic simulations
"""

NM_PRODUCT_CATALOG = {
    "Life Insurance": [
        {
            "name": "Term 10",
            "type": "Term Life",
            "desc": "10-year level term life insurance. Lowest premium, convertible to permanent coverage."
        },
        {
            "name": "Term 20",
            "type": "Term Life",
            "desc": "20-year level term life insurance. Popular for mortgage/income protection during working years."
        },
        {
            "name": "Term 80 (ART)",
            "type": "Term Life",
            "desc": "Annual Renewable Term to age 80. Premiums increase annually. Maximum flexibility."
        },
        {
            "name": "Whole Life Plus",
            "type": "Permanent Life",
            "desc": "Flagship whole life with guaranteed cash value growth, dividends, and lifetime coverage."
        },
        {
            "name": "65 Life",
            "type": "Permanent Life",
            "desc": "Whole Life paid-up at age 65. Premium paying period ends at retirement."
        },
        {
            "name": "90 Life",
            "type": "Permanent Life",
            "desc": "Whole Life paid-up at age 90. Lower premiums, longer payment period."
        },
        {
            "name": "Survivorship Whole Life",
            "type": "Permanent Life",
            "desc": "Covers two lives (typically spouses), pays on second death. Estate tax planning tool."
        },
        {
            "name": "Custom Universal Life (CUL)",
            "type": "Universal Life",
            "desc": "Flexible premium UL with guaranteed death benefit. Adjustable coverage and payments."
        },
        {
            "name": "Variable Universal Life (VUL)",
            "type": "Universal Life",
            "desc": "UL with investment sub-accounts. Cash value growth linked to market performance."
        },
        {
            "name": "Single Premium Whole Life",
            "type": "Permanent Life",
            "desc": "One-time lump sum payment. Immediate cash value and lifetime coverage."
        }
    ],
    "Disability Income": [
        {
            "name": "Disability Income Insurance (Own Occupation)",
            "type": "Income Replacement",
            "desc": "True own-occupation definition. Replaces 60-70% of income if unable to perform your specific job."
        },
        {
            "name": "Overhead Expense Insurance",
            "type": "Business Protection",
            "desc": "Reimburses business overhead expenses (rent, salaries, utilities) during owner's disability."
        },
        {
            "name": "Business Disability Buyout",
            "type": "Business Protection",
            "desc": "Funds business partner buyout if owner becomes permanently disabled."
        }
    ],
    "Long-Term Care": [
        {
            "name": "Long-Term Care Insurance",
            "type": "LTC",
            "desc": "Standalone LTC coverage for nursing home, assisted living, or home care expenses."
        },
        {
            "name": "Accelerated Care Benefit (Hybrid Life/LTC)",
            "type": "Hybrid LTC",
            "desc": "Whole life policy with LTC rider. Accelerates death benefit for qualifying care expenses."
        }
    ],
    "Annuities": [
        {
            "name": "Single Premium Immediate Annuity (SPIA)",
            "type": "Income Annuity",
            "desc": "Lump sum conversion to guaranteed lifetime income. Payments start within 1 year."
        },
        {
            "name": "Deferred Income Annuity (DIA)",
            "type": "Income Annuity",
            "desc": "Purchase now, income starts at future date. Longevity insurance for late retirement."
        },
        {
            "name": "Fixed Rate Annuity",
            "type": "Accumulation Annuity",
            "desc": "Guaranteed fixed interest rate for set period. Tax-deferred CD alternative."
        },
        {
            "name": "Variable Annuity",
            "type": "Accumulation Annuity",
            "desc": "Tax-deferred growth with investment options. Optional living benefit riders."
        },
        {
            "name": "Index Annuity",
            "type": "Accumulation Annuity",
            "desc": "Growth linked to market index with downside protection. Balanced risk/reward."
        }
    ],
    "Wealth Management": [
        {
            "name": "Brokerage Account",
            "type": "Investment",
            "desc": "Self-directed or advisor-assisted trading. Access to stocks, bonds, mutual funds, ETFs."
        },
        {
            "name": "Advisory Account",
            "type": "Managed Investment",
            "desc": "Fee-based professionally managed portfolio. Customized asset allocation."
        },
        {
            "name": "Private Client Services",
            "type": "Premium Wealth",
            "desc": "High-net-worth comprehensive planning. Estate, tax, philanthropic strategies."
        },
        {
            "name": "Roth IRA",
            "type": "Retirement",
            "desc": "Post-tax contributions, tax-free growth and qualified withdrawals. No RMDs."
        },
        {
            "name": "Traditional IRA",
            "type": "Retirement",
            "desc": "Pre-tax contributions, tax-deferred growth. RMDs at age 73."
        },
        {
            "name": "529 College Savings Plan",
            "type": "Education",
            "desc": "Tax-advantaged savings for qualified education expenses. State tax deduction available."
        }
    ]
}


def get_product_catalog_text() -> str:
    """
    Returns formatted catalog text for LLM prompt inclusion.
    
    Returns:
        Markdown-formatted string listing all available products
    """
    catalog_text = "**NORTHWESTERN MUTUAL PRODUCT PORTFOLIO (Select ONLY from this list):**\n\n"
    
    for category, products in NM_PRODUCT_CATALOG.items():
        catalog_text += f"### {category}\n"
        for product in products:
            catalog_text += f"- **{product['name']}** ({product['type']}): {product['desc']}\n"
        catalog_text += "\n"
    
    return catalog_text


def get_product_count() -> int:
    """Returns total number of products in catalog."""
    return sum(len(products) for products in NM_PRODUCT_CATALOG.values())


# Validation
if __name__ == "__main__":
    print(f"Total Products: {get_product_count()}")
    print("\n" + "="*70)
    print(get_product_catalog_text())
