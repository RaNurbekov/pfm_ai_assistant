import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from kz_categorizer import categorize_transaction_kz

# ── KZ Merchant Database ──────────────────────────────────
KZ_MERCHANTS = {
    'Food & Dining': [
        ('GLOVO*ORDER', 3500, 15000),
        ('WOLT DELIVERY', 2500, 12000),
        ('KFC ALMATY', 2000, 8000),
        ('BURGER KING KZ', 1500, 6000),
        ('CHOCOFOOD ORDER', 3000, 10000),
        ('MCDONALDS ALMATY', 1200, 5000),
        ('LOCAL CAFE', 800, 4000),
    ],
    'Shopping': [
        ('KASPI SHOP PURCHASE', 5000, 150000),
        ('WILDBERRIES KZ', 3000, 80000),
        ('MAGNUM SUPERMARKET', 5000, 30000),
        ('SMALL SUPERMARKET', 2000, 15000),
        ('SULPAK ELECTRONICS', 20000, 200000),
        ('TECHNODOM KZ', 15000, 300000),
        ('METRO CASH AND CARRY', 10000, 50000),
    ],
    'Transport': [
        ('INDRIVE TRIP', 500, 3000),
        ('YANDEX GO RIDE', 600, 4000),
        ('AIR ASTANA TICKET', 30000, 200000),
        ('FLY ARYSTAN', 15000, 80000),
        ('KTZ RAILWAY TICKET', 5000, 25000),
        ('АЗС HELIOS PETROL', 8000, 20000),
        ('АЗС SINOOIL FUEL', 7000, 18000),
    ],
    'Utilities': [
        ('KCELL PAYMENT', 2000, 5000),
        ('BEELINE KZ RECHARGE', 1500, 4000),
        ('TELE2 KZ PAYMENT', 1200, 3500),
        ('KAZAKHTELECOM INTERNET', 4000, 8000),
        ('ALMATY ENERGO ELECTRIC', 5000, 15000),
        ('ВОДОКАНАЛ PAYMENT', 2000, 6000),
        ('ЖКХ КОММУНАЛКА', 15000, 40000),
    ],
    'Entertainment': [
        ('KINOPARK TICKET', 2000, 5000),
        ('CHAPLIN CINEMA', 1800, 4500),
        ('NETFLIX SUBSCRIPTION', 4990, 4990),
        ('SPOTIFY PREMIUM', 1490, 1490),
        ('YOUTUBE PREMIUM', 990, 990),
        ('STEAM GAMES', 2000, 30000),
    ],
    'Healthcare': [
        ('INVIVO CLINIC', 5000, 30000),
        ('OLYMPIC PLUS CLINIC', 8000, 50000),
        ('APTEKA 36.6', 1000, 15000),
        ('APTEKA SAINT LUKE', 500, 10000),
        ('MEDICALCENTER KZ', 10000, 80000),
    ],
    'Education': [
        ('COURSERA SUBSCRIPTION', 15000, 15000),
        ('UDEMY COURSE', 5000, 20000),
        ('SKILLBOX KZ', 20000, 60000),
        ('UNIVERSITY TUITION', 100000, 300000),
    ],
    'Loan & Finance': [
        ('KASPI KREDIT PAYMENT', 20000, 100000),
        ('HALYK FINANCE LOAN', 30000, 150000),
        ('FREEDOM FINANCE EMI', 15000, 80000),
        ('INSURANCE PAYMENT', 5000, 20000),
    ]
}

# ── Customer Profiles ─────────────────────────────────────
PROFILES = {
    'Student (18-23)': {
        'monthly_income': 80_000,
        'income_source': 'СТИПЕНДИЯ + ПОДРАБОТКА',
        'spending_weights': {
            'Food & Dining': 0.35,
            'Transport': 0.20,
            'Entertainment': 0.20,
            'Shopping': 0.15,
            'Utilities': 0.10,
        },
        'tx_per_month': 40
    },
    'Young Professional (25-30)': {
        'monthly_income': 350_000,
        'income_source': 'SALARY KASPI BANK',
        'spending_weights': {
            'Food & Dining': 0.20,
            'Shopping': 0.20,
            'Transport': 0.15,
            'Utilities': 0.12,
            'Entertainment': 0.10,
            'Loan & Finance': 0.13,
            'Healthcare': 0.05,
            'Education': 0.05,
        },
        'tx_per_month': 80
    },
    'Family (35-45)': {
        'monthly_income': 600_000,
        'income_source': 'SALARY HALYK BANK',
        'spending_weights': {
            'Shopping': 0.25,
            'Utilities': 0.20,
            'Food & Dining': 0.15,
            'Education': 0.12,
            'Transport': 0.10,
            'Healthcare': 0.10,
            'Loan & Finance': 0.08,
        },
        'tx_per_month': 100
    }
}

# ── Seasonal multipliers ──────────────────────────────────
SEASONAL = {
    1: 0.85,   # January — post holiday savings
    2: 0.90,
    3: 0.95,
    4: 1.00,
    5: 1.05,
    6: 1.10,   # Summer — more spending
    7: 1.15,
    8: 1.10,
    9: 1.00,   # Back to school
    10: 1.00,
    11: 1.10,
    12: 1.40,  # December — holiday season spike
}

def generate_kz_transactions(profile_name, months=12):
    profile = PROFILES[profile_name]
    transactions = []
    
    start_date = datetime(2024, 1, 1)
    account_no = f"KZ{random.randint(10000000000, 99999999999)}"
    balance = profile['monthly_income'] * 2
    
    for month in range(months):
        current_date = start_date + timedelta(days=30 * month)
        seasonal_factor = SEASONAL[current_date.month]
        
        # ── Monthly salary ────────────────────────────────
        salary_date = current_date + timedelta(days=random.randint(1, 5))
        salary = profile['monthly_income'] * random.uniform(0.95, 1.05)
        balance += salary
        
        transactions.append({
            'Account No': account_no,
            'DATE': salary_date,
            'TRANSACTION DETAILS': profile['income_source'],
            'VALUE DATE': salary_date,
            'BALANCE AMT': round(balance, 2),
            'AMOUNT': round(salary, 2),
            'TYPE': 'CREDIT',
            'CATEGORY': 'Income'
        })
        
        # ── Monthly spending ──────────────────────────────
        monthly_budget = salary * 0.80
        tx_count = int(profile['tx_per_month'] * seasonal_factor)
        
        for _ in range(tx_count):
            # Pick random category based on weights
            categories = list(profile['spending_weights'].keys())
            weights = list(profile['spending_weights'].values())
            category = random.choices(categories, weights=weights)[0]
            
            # Pick random merchant from category
            if category in KZ_MERCHANTS:
                merchant_data = random.choice(KZ_MERCHANTS[category])
                merchant_name, min_amt, max_amt = merchant_data
                
                amount = random.uniform(min_amt, max_amt) * seasonal_factor
                amount = min(amount, monthly_budget * 0.3)
                
                tx_date = current_date + timedelta(
                    days=random.randint(0, 28)
                )
                balance -= amount
                
                transactions.append({
                    'Account No': account_no,
                    'DATE': tx_date,
                    'TRANSACTION DETAILS': merchant_name,
                    'VALUE DATE': tx_date,
                    'BALANCE AMT': round(balance, 2),
                    'AMOUNT': round(-amount, 2),
                    'TYPE': 'DEBIT',
                    'CATEGORY': category
                })
        
        # ── Random anomaly (1 per 3 months) ──────────────
        if month % 3 == 0:
            anomaly_amount = profile['monthly_income'] * random.uniform(0.5, 1.5)
            anomaly_date = current_date + timedelta(days=random.randint(1, 28))
            balance -= anomaly_amount
            
            transactions.append({
                'Account No': account_no,
                'DATE': anomaly_date,
                'TRANSACTION DETAILS': 'UNUSUAL LARGE TRANSACTION',
                'VALUE DATE': anomaly_date,
                'BALANCE AMT': round(balance, 2),
                'AMOUNT': round(-anomaly_amount, 2),
                'TYPE': 'DEBIT',
                'CATEGORY': 'Other'
            })
    
    df = pd.DataFrame(transactions)
    df = df.sort_values('DATE').reset_index(drop=True)
    return df

def generate_all_profiles(months=12):
    all_data = []
    for profile_name in PROFILES.keys():
        print(f"Generating {profile_name}...")
        df = generate_kz_transactions(profile_name, months)
        all_data.append(df)
        print(f"  → {len(df)} transactions generated")
    
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv('kz_transactions.csv', index=False)
    print(f"\n✅ Total: {len(combined)} KZ transactions saved!")
    print(f"Profiles: {combined['Account No'].nunique()} accounts")
    return combined

if __name__ == "__main__":
    df = generate_all_profiles(months=12)
    print(df.head(10))
    print(df['CATEGORY'].value_counts())