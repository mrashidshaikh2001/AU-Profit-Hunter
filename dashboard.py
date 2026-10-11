
import streamlit as st
import pandas as pd

from profit_calculator import calculate_profit


st.set_page_config(
    page_title="AU Profit Hunter",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 AU Profit Hunter")
st.caption(
    "Multi-region product research | "
    "Australia launch | Listing drafts only"
)

st.info(
    "Demo mode: these are sample products, not live marketplace data. "
    "Do not use these figures to make real purchasing decisions."
)

with st.sidebar:
    st.header("Research settings")
    marketplace = st.selectbox(
        "Marketplace",
        ["Australia (AUD)", "United States (USD)", "United Kingdom (GBP)"],
    )
    minimum_profit = st.number_input(
        "Minimum net profit",
        min_value=0.0,
        value=2.0,
        step=0.5,
    )
    st.caption(
        "The EU and additional marketplaces will be added later. "
        "Each region needs its own verified fees and supplier data."
    )

currency = {
    "Australia (AUD)": "AUD",
    "United States (USD)": "USD",
    "United Kingdom (GBP)": "GBP",
}[marketplace]

samples = [
    {
        "Product": "Example cable clips",
        "Sale price": 30.00,
        "Supplier cost": 20.00,
        "Shipping": 0.00,
        "Returns allowance": 0.50,
    },
    {
        "Product": "Example travel organiser",
        "Sale price": 25.00,
        "Supplier cost": 20.00,
        "Shipping": 1.00,
        "Returns allowance": 0.50,
    },
    {
        "Product": "Example pet grooming tool",
        "Sale price": 35.00,
        "Supplier cost": 22.00,
        "Shipping": 3.00,
        "Returns allowance": 1.00,
    },
]

results = []

for item in samples:
    result = calculate_profit(
        sale_price=item["Sale price"],
        product_cost=item["Supplier cost"],
        seller_shipping=item["Shipping"],
        return_allowance=item["Returns allowance"],
        currency=currency,
    )

    profit = result.net_profit

    results.append({
        **item,
        "Marketplace fees": float(result.ebay_fees),
        "Estimated net profit": float(profit),
        "Profit margin (%)": float(result.profit_margin_percent),
        "Decision": (
            "PASS"
            if profit >= minimum_profit
            else "REJECT"
        ),
        "Data status": "SAMPLE ONLY",
    })

df = pd.DataFrame(results)

pass_count = int(
    (df["Estimated net profit"] >= minimum_profit).sum()
)

col1, col2, col3 = st.columns(3)

col1.metric("Sample products", len(df))
col2.metric("Candidates passing target", pass_count)
col3.metric("Minimum profit", f"{currency} {minimum_profit:.2f}")

st.subheader("Product candidates")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Test a product yourself")

with st.form("profit_calculator_form"):
    product_name = st.text_input(
        "Product name",
        value="My test product",
    )

    col1, col2 = st.columns(2)

    with col1:
        sale_price = st.number_input(
            "Expected sale price",
            min_value=0.01,
            value=30.00,
            step=1.00,
        )
        supplier_cost = st.number_input(
            "Supplier product cost",
            min_value=0.00,
            value=20.00,
            step=1.00,
        )
        shipping = st.number_input(
            "Seller-paid shipping",
            min_value=0.00,
            value=0.00,
            step=0.50,
        )

    with col2:
        return_allowance = st.number_input(
            "Returns allowance",
            min_value=0.00,
            value=0.50,
            step=0.50,
        )
        advertising = st.number_input(
            "Advertising cost per order",
            min_value=0.00,
            value=0.00,
            step=0.50,
        )
        other_costs = st.number_input(
            "Other costs per order",
            min_value=0.00,
            value=0.00,
            step=0.50,
        )

    submitted = st.form_submit_button("Calculate profit")

if submitted:
    try:
        result = calculate_profit(
            sale_price=sale_price,
            product_cost=supplier_cost,
            seller_shipping=shipping,
            return_allowance=return_allowance,
            advertising=advertising,
            other_costs=other_costs,
            currency=currency,
        )

        st.subheader(f"Result: {product_name or 'Unnamed product'}")
        st.metric(
            "Estimated net profit",
            f"{currency} {result.net_profit:.2f}",
        )
        st.metric(
            "Estimated profit margin",
            f"{result.profit_margin_percent:.2f}%",
        )

        if result.net_profit >= minimum_profit:
            st.success(
                "Passes your selected profit target under the current "
                "fee assumptions. This is not a purchase recommendation."
            )
        else:
            st.error(
                "Reject this candidate: estimated profit is below "
                "your selected minimum."
            )

        st.caption(
            "Fee assumption currently uses 19.35% + 0.30 in the "
            "selected currency. Verify actual marketplace fees before "
            "using this estimate. Taxes, currency conversion, supplier "
            "stock and fulfilment eligibility are not verified here."
        )

    except ValueError as error:
        st.error(str(error))

st.warning(
    "No live product discovery or listing publication is enabled. "
    "All displayed products are examples. Listing approval remains manual."
)
