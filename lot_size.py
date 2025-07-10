def calculate_lot_size(account_balance, risk_percentage, pip_value, stop_loss_pips):
    risk_amount = account_balance * (risk_percentage / 100)
    dollar_per_pip = pip_value
    lot_size = risk_amount / (dollar_per_pip * stop_loss_pips)
    
    # Ensure the lot size is at least 0.01 lots
    lot_size = max(lot_size, 0.01)
    
    # Round the lot size to 2 decimals
    lot_size = round(lot_size, 2)
    
    return lot_size

# Example usage:
# account_balance = 5678  # Replace with your actual account balance
# risk_percentage = 2  # Replace with your desired risk percentage
# pip_value = 10  # Replace with your actual pip value
# stop_loss_pips = 150  # Replace with your desired stop loss in pips

# lot_size = calculate_lot_size(account_balance, risk_percentage, pip_value, stop_loss_pips)

# print(f"Account Balance: ${account_balance}")
# print(f"Risk Percentage: {risk_percentage}%")
# print(f"Pip Value: ${pip_value}")
# print(f"Stop Loss: {stop_loss_pips} pips")
# print(f"Calculated Lot Size: {lot_size} lots")
