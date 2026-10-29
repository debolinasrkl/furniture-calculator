# ---------------------------------------------------------------
# Furniture Cost Calculator  |  Python Programming for Business Students
# A simple Streamlit website that helps a customer of a furniture store
# find the TOTAL price of an order (with discounts, add-ons, delivery and GST)
# before visiting the store.
# Run with:  streamlit run app.py
# ---------------------------------------------------------------

import streamlit as st  # Streamlit turns our Python script into a website

# ---------------------------------------------------------------
# 1. STORE DATA (dictionaries store "name -> value" pairs)
# ---------------------------------------------------------------

# Base price (float/int, in rupees) of ONE piece of each furniture type
furniture_prices = {
    "Sofa (3-Seater)": 25000,
    "Double Bed": 30000,
    "Dining Table (6-Seater)": 22000,
    "Wardrobe": 18000,
    "Study Table": 8000,
    "Office Chair": 6000,
    "Bookshelf": 7500,
    "TV Unit": 9500,
}

# Material multiplier: premium materials make the base price higher
material_multipliers = {
    "Engineered Wood": 1.0,   # standard price
    "Metal Frame": 1.2,       # 20% costlier
    "Sheesham Wood": 1.4,     # 40% costlier
    "Teak Wood": 1.8,         # 80% costlier
}

# Delivery options and their charges (in rupees)
delivery_charges = {
    "Store Pickup (Free)": 0,
    "Standard Delivery (3-5 days)": 1500,
    "Express Delivery (1-2 days)": 3000,
}

# Extra charges per piece for optional services
ASSEMBLY_COST_PER_ITEM = 800      # fitting/assembly at home
WARRANTY_COST_PER_ITEM = 1000     # 2-year extended warranty
GST_RATE = 0.18                   # 18% GST on the final taxable amount
FREE_DELIVERY_LIMIT = 75000       # delivery is free above this amount


# ---------------------------------------------------------------
# 2. FUNCTION: does all the business calculation
# ---------------------------------------------------------------
def calculate_bill(item, material, quantity, customer, delivery, assembly, warranty):
    """Takes the customer's choices and returns a dictionary of all amounts."""

    # Price of one piece = base price x material multiplier
    unit_price = furniture_prices[item] * material_multipliers[material]

    # Base cost of the whole order
    base_cost = unit_price * quantity

    # Bulk discount: more pieces = bigger discount (if / elif / else)
    if quantity >= 10:
        bulk_discount_pct = 15
    elif quantity >= 5:
        bulk_discount_pct = 10
    elif quantity >= 3:
        bulk_discount_pct = 5
    else:
        bulk_discount_pct = 0

    # Customer-type discount (loyal customers and students save extra)
    if customer == "Loyalty Member":
        customer_discount_pct = 8
    elif customer == "Student":
        customer_discount_pct = 5
    else:
        customer_discount_pct = 0

    # Total discount = bulk + customer discount, applied on the base cost
    total_discount_pct = bulk_discount_pct + customer_discount_pct
    discount_amount = base_cost * total_discount_pct / 100
    cost_after_discount = base_cost - discount_amount

    # Optional add-ons are charged per piece (bool checkboxes decide)
    addon_cost = 0
    if assembly:
        addon_cost += ASSEMBLY_COST_PER_ITEM * quantity
    if warranty:
        addon_cost += WARRANTY_COST_PER_ITEM * quantity

    # Delivery is free if the discounted order is big enough
    if cost_after_discount >= FREE_DELIVERY_LIMIT:
        delivery_cost = 0
    else:
        delivery_cost = delivery_charges[delivery]

    # GST is charged on everything the customer pays for
    taxable_amount = cost_after_discount + addon_cost + delivery_cost
    gst = taxable_amount * GST_RATE
    total = taxable_amount + gst

    # Send all the numbers back as one dictionary
    return {
        "unit_price": unit_price,
        "base_cost": base_cost,
        "bulk_discount_pct": bulk_discount_pct,
        "customer_discount_pct": customer_discount_pct,
        "discount_amount": discount_amount,
        "cost_after_discount": cost_after_discount,
        "addon_cost": addon_cost,
        "delivery_cost": delivery_cost,
        "gst": gst,
        "total": total,
    }


# ---------------------------------------------------------------
# 3. WEBSITE LAYOUT (what the customer sees)
# ---------------------------------------------------------------
st.set_page_config(page_title="Furniture Cost Calculator", page_icon="🛋️")
st.title("🛋️ Furniture Cost Calculator")
st.write("Choose your furniture and get the **total price instantly** - "
         "including discounts, delivery and GST.")

# Sidebar: a loop prints the price list so customers can compare
with st.sidebar:
    st.header("Price List (per piece)")
    for name, price in furniture_prices.items():
        st.write(f"{name}: ₹{price:,}")
    st.caption("Material changes the price: Metal x1.2, Sheesham x1.4, Teak x1.8")

# ---- USER INPUTS (7 different widgets) ----
col1, col2 = st.columns(2)

with col1:
    # Input 1 (str): furniture type from a dropdown
    item = st.selectbox("Furniture Type", list(furniture_prices.keys()))
    # Input 2 (str): material from a dropdown
    material = st.selectbox("Material", list(material_multipliers.keys()))
    # Input 3 (int): number of pieces (0 is allowed so we can show a warning)
    quantity = st.number_input("Quantity", min_value=0, max_value=100, value=1, step=1)
    # Input 4 (str): customer type for the discount
    customer = st.selectbox("Customer Type", ["Regular", "Student", "Loyalty Member"])

with col2:
    # Input 5 (str): how the furniture reaches the customer
    delivery = st.radio("Delivery Option", list(delivery_charges.keys()))
    # Input 6 (bool): assembly service
    assembly = st.checkbox(f"Home Assembly (+₹{ASSEMBLY_COST_PER_ITEM}/piece)")
    # Input 7 (bool): extended warranty
    warranty = st.checkbox(f"2-Year Extended Warranty (+₹{WARRANTY_COST_PER_ITEM}/piece)")

# ---------------------------------------------------------------
# 4. CALCULATE AND SHOW RESULT (with error handling)
# ---------------------------------------------------------------
if st.button("Calculate Total"):
    # Input validation: quantity must be at least 1
    if quantity <= 0:
        st.warning("Please enter a quantity of at least 1.")
    else:
        try:
            # Call our function with the customer's choices
            bill = calculate_bill(item, material, int(quantity), customer,
                                  delivery, assembly, warranty)

            st.subheader("Your Bill")
            st.write(f"**{item}** in **{material}** at ₹{bill['unit_price']:,.2f} each "
                     f"x {int(quantity)} piece(s)")

            # Show the step-by-step breakdown line by line
            st.write(f"Base cost: ₹{bill['base_cost']:,.2f}")
            st.write(f"Discount ({bill['bulk_discount_pct']}% bulk + "
                     f"{bill['customer_discount_pct']}% customer): "
                     f"-₹{bill['discount_amount']:,.2f}")
            st.write(f"Add-ons (assembly / warranty): ₹{bill['addon_cost']:,.2f}")

            # Tell the customer if delivery became free
            if bill["delivery_cost"] == 0 and delivery != "Store Pickup (Free)":
                st.write("Delivery: ₹0.00 (free on large orders!)")
            else:
                st.write(f"Delivery: ₹{bill['delivery_cost']:,.2f}")

            st.write(f"GST (18%): ₹{bill['gst']:,.2f}")

            # Final amount shown in a green success box
            st.success(f"Total Amount Payable: ₹{bill['total']:,.2f}")

        except Exception as error:
            # If anything unexpected happens, show a friendly message (no crash)
            st.error(f"Sorry, something went wrong: {error}")
