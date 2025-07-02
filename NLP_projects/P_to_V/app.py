import streamlit as st
import random

st.title("🎯 The Rigged Betting Game")

st.markdown(
    """
    Bet on **Heads** or **Tails**. Win money!  
    
    """
)

# Initialize session state
if 'balance' not in st.session_state:
    st.session_state.balance = 1000  # Starting money

if 'rounds' not in st.session_state:
    st.session_state.rounds = 0

# Show balance and get user input
st.markdown(f"**Current Balance:** 💰 ${st.session_state.balance}")
bet_amount = st.slider("Bet amount:", 1, 500, 100)
choice = st.radio("Choose your side:", ["Heads", "Tails"])

# Betting logic
if st.button("Flip the Coin"):
    st.session_state.rounds += 1

    # Fair play for first 5 rounds
    if st.session_state.rounds <= 10:
        result = random.choice(["Heads", "Tails"])
    else:
        # The trap: Flip result is always the opposite of user choice
        result = "Tails" if choice == "Heads" else "Heads"

    st.write(f"🪙 The coin landed on: **{result}**")

    if choice == result:
        st.success(f"You won ${bet_amount}!")
        st.session_state.balance += bet_amount
    else:
        st.error(f"You lost ${bet_amount}.")
        st.session_state.balance -= bet_amount

    if st.session_state.balance <= 0:
        st.warning("💀 You're broke! Refresh to try again.")
        # st.stop()

    st.markdown(f"**Round:** {st.session_state.rounds}")

# Optional reset button
if st.button("🔄 Reset Game"):
    st.session_state.balance < 0
    st.session_state.rounds = 0
    st.success("Game has been reset.")
