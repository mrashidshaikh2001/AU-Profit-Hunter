
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP


MONEY = Decimal("0.01")
MINIMUM_NET_PROFIT = Decimal("2.00")


def money(value):
    """Convert an input to a safely rounded monetary amount."""
    return Decimal(str(value)).quantize(
        MONEY, rounding=ROUND_HALF_UP
    )


@dataclass
class ProfitResult:
    currency: str
    sale_price: Decimal
    ebay_fees: Decimal
    product_cost: Decimal
    seller_shipping: Decimal
    advertising: Decimal
    return_allowance: Decimal
    other_costs: Decimal
    net_profit: Decimal
    profit_margin_percent: Decimal
    qualifies: bool
    reason: str


def calculate_profit(
    sale_price,
    product_cost,
    seller_shipping=0,
    fee_rate="0.1935",
    fixed_fee="0.30",
    advertising=0,
    return_allowance=0,
    other_costs=0,
    currency="AUD",
):
    """
    Estimate net profit for one order.

    All amounts must use the same currency.
    Fee settings are configurable assumptions, not
    a guarantee of the actual marketplace fees.
    """
    values = {
        "sale_price": sale_price,
        "product_cost": product_cost,
        "seller_shipping": seller_shipping,
        "fee_rate": fee_rate,
        "fixed_fee": fixed_fee,
        "advertising": advertising,
        "return_allowance": return_allowance,
        "other_costs": other_costs,
    }

    for name, value in values.items():
        if not Decimal(str(value)).is_finite():
            raise ValueError(f"{name} must be a finite number")

    price = money(sale_price)
    cost = money(product_cost)
    shipping = money(seller_shipping)
    ad_cost = money(advertising)
    returns = money(return_allowance)
    other = money(other_costs)
    rate = Decimal(str(fee_rate))
    fixed = money(fixed_fee)

    if not rate.is_finite() or not Decimal("0") <= rate <= Decimal("1"):
        raise ValueError("fee_rate must be between 0 and 1")

    if price <= 0:
        raise ValueError("sale_price must be greater than zero")

    if min(cost, shipping, ad_cost, returns, other, fixed) < 0:
        raise ValueError("Costs cannot be negative")

    if not currency or len(currency) != 3 or not currency.isalpha():
        raise ValueError("currency must be a three-letter code")

    fees = money(price * rate + fixed)
    profit = money(
        price - fees - cost - shipping - ad_cost - returns - other
    )
    margin = (profit / price * 100).quantize(
        MONEY, rounding=ROUND_HALF_UP
    )

    qualifies = profit >= MINIMUM_NET_PROFIT

    return ProfitResult(
        currency=currency.upper(),
        sale_price=price,
        ebay_fees=fees,
        product_cost=cost,
        seller_shipping=shipping,
        advertising=ad_cost,
        return_allowance=returns,
        other_costs=other,
        net_profit=profit,
        profit_margin_percent=margin,
        qualifies=qualifies,
        reason=(
            "Meets minimum profit target"
            if qualifies
            else "Rejected: net profit is below the minimum target"
        ),
    )


if __name__ == "__main__":
    result = calculate_profit(
        sale_price="30.00",
        product_cost="20.00",
        seller_shipping="0.00",
        advertising="0.00",
        return_allowance="0.50",
        other_costs="0.00",
    )

    for key, value in asdict(result).items():
        print(f"{key}: {value}")
