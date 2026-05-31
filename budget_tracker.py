import pandas as pd
import json
import os

BUDGET_FILE = 'budgets.json'

def load_budgets():
    """Load saved budgets from JSON file"""
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_budgets(budgets):
    """Save budgets to JSON file"""
    with open(BUDGET_FILE, 'w') as f:
        json.dump(budgets, f, indent=2)

def calculate_spending_vs_budget(filtered_df, budgets, currency='₸'):
    """Calculate actual spending vs budget per category"""
    
    EXCLUDE = ['Transfer', 'ATM & Cash', 'Other']
    
    real_spending = filtered_df[
        (filtered_df['TYPE'] == 'DEBIT') &
        (~filtered_df['CATEGORY'].isin(EXCLUDE))
    ]
    
    actual_by_category = (
        real_spending
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .reset_index()
    )
    actual_by_category.columns = ['CATEGORY', 'ACTUAL']
    
    results = []
    
    for _, row in actual_by_category.iterrows():
        category = row['CATEGORY']
        actual = row['ACTUAL']
        budget = budgets.get(category, 0)
        
        if budget > 0:
            pct_used = (actual / budget) * 100
            remaining = budget - actual
            status = (
                '🔴 Over Budget' if pct_used > 100 else
                '🟠 Warning' if pct_used > 80 else
                '🟡 On Track' if pct_used > 50 else
                '🟢 Good'
            )
        else:
            pct_used = 0
            remaining = 0
            status = '⚪ No Budget Set'
        
        results.append({
            'Category': category,
            'Budget': budget,
            'Actual': actual,
            'Remaining': remaining,
            'Used %': pct_used,
            'Status': status
        })
    
    # Add categories with budget but no spending
    for category, budget in budgets.items():
        if category not in actual_by_category['CATEGORY'].values:
            results.append({
                'Category': category,
                'Budget': budget,
                'Actual': 0,
                'Remaining': budget,
                'Used %': 0,
                'Status': '🟢 Good'
            })
    
    return pd.DataFrame(results).sort_values('Used %', ascending=False)