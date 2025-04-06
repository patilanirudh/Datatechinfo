# import streamlit as st
# import numpy as np
# import plotly.express as px #for graph plotting

# #app title
# st.title("First Streamlit APP")

# #user input
# num=st.number_input("enter a number",value=1)

# sq=num**2

# # output 
# st.write(f"squared value:{sq}")

# x=np.linspace(0,num,100) #creates 100 data points from 0 to num
# y=x**2
# fig=px.line(x=x,y=y,labels={'x':'i/p','y':'sq o/p'})

# #graph of squares
# st.plotly_chart(fig)


import streamlit as st
import plotly.express as px
import numpy as np

# Streamlit UI
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.title("💰 Personal Finance Tracker (INR)")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.header("Enter Your Monthly Income & Expenses")
    income = st.number_input("Your Total Monthly Income (₹)", min_value=0.0, format="%.2f")
    rent = st.number_input("Rent (₹)", min_value=0.0, format="%.2f")
    food = st.number_input("Food Expenses (₹)", min_value=0.0, format="%.2f")
    travel = st.number_input("Travel Expenses (₹)", min_value=0.0, format="%.2f")
    other_expenses = st.number_input("Other Expenses (₹)", min_value=0.0, format="%.2f")
    calculate = st.button("💡 Calculate Insights")

if calculate:
    total_expense = rent + food + travel + other_expenses
    savings = income - total_expense
    
    with col2:
        st.subheader("📈 Financial Summary")
        st.metric("Total Expenses", f"₹{total_expense:.2f}")
        st.metric("Savings", f"₹{savings:.2f}", delta=savings)
    
    st.markdown("---")
    
    # Expense Breakdown Pie Chart
    st.subheader("📊 Expense Breakdown")
    expense_labels = ["Rent", "Food", "Travel", "Other"]
    expense_values = [rent, food, travel, other_expenses]
    fig_pie = px.pie(names=expense_labels, values=expense_values, title="Expense Distribution", hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Income vs Expenses Bar Chart
    st.subheader("📊 Income vs. Expenses")
    categories = ["Income", "Expenses"]
    values = [income, total_expense]
    fig_bar = px.bar(x=categories, y=values, title="Income vs. Expenses", labels={"x": "Category", "y": "Amount (₹)"}, color=categories)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Future Savings Projection with Visible Labels
    st.subheader("📈 Future Savings Projection")
    months = np.arange(1, 13)
    future_savings = np.cumsum([savings] * 12)
    fig_line = px.line(x=months, y=future_savings, labels={"x": "Months", "y": "Projected Savings (₹)"}, title="Projected Savings for Next 12 Months", markers=True)
    
    # Make savings amount visible by default with annotations
    fig_line.update_traces(marker=dict(color='darkblue'))
    for i, value in enumerate(future_savings):
        fig_line.add_annotation(x=months[i], y=value, text=f"₹{value:.2f}", showarrow=True, arrowhead=2, font=dict(color="darkblue"))
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Insights & Saving Suggestions
    st.markdown("---")
    st.subheader("💡 Financial Insights & Saving Suggestions")
    if savings < 0:
        st.warning("🚨 Your expenses exceed your income! Consider reducing discretionary spending.")
    elif savings < 0.2 * income:
        st.info("🔹 Your savings are low. Try to save at least 20% of your income.")
    else:
        st.success("✅ Great! You have a healthy savings ratio.")
    
    if food > 0.3 * income:
        st.warning("🍽️ High food expenses detected! Consider meal planning or home cooking to save money.")
    if travel > 0.2 * income:
        st.warning("🚗 Travel expenses seem high. Explore public transport or carpooling options.")
    if rent > 0.4 * income:
        st.warning("🏠 Rent is consuming a significant part of your income. Consider renegotiating or moving to a cheaper location.")
    
    st.markdown("### 💰 Saving Options")
    st.info("- **Fixed Deposits (FDs):** Secure way to earn interest on savings.\n- **Mutual Funds:** SIPs for long-term wealth growth.\n- **Gold Investments:** Hedge against inflation.\n- **Recurring Deposits (RDs):** Ideal for disciplined savings.")