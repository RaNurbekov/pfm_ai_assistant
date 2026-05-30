import pandas as pd
import numpy as np
from scipy import stats


def detect_anomalies(df, sensitivity=2.0):
    df = df.copy()
    df['ANOMALY'] = False
    df['ANOMALY_REASON'] = ''
    df['ANOMALY_SCORE'] = 0.0

    # ── Method 1: Z-Score per category ───────────────────
    for category in df[df['TYPE'] == 'DEBIT']['CATEGORY'].unique():
        cat_mask = (df['TYPE'] == 'DEBIT') & (df['CATEGORY'] == category)
        cat_amounts = df.loc[cat_mask, 'AMOUNT'].abs()

        if len(cat_amounts) > 3:
            z_scores = np.abs(stats.zscore(cat_amounts))
            anomaly_indices = cat_amounts[z_scores > sensitivity].index

            df.loc[anomaly_indices, 'ANOMALY'] = True
            df.loc[anomaly_indices, 'ANOMALY_SCORE'] += 3.0
            df.loc[anomaly_indices, 'ANOMALY_REASON'] += \
                f'Amount {sensitivity}x above {category} average | '

    # ── Method 2: New Category ────────────────────────────
    df_sorted = df.sort_values('DATE')
    seen_categories = set()

    for idx, row in df_sorted.iterrows():
        if row['TYPE'] == 'DEBIT':
            if row['CATEGORY'] not in seen_categories and \
               row['CATEGORY'] not in ['Transfer', 'ATM & Cash', 'Other']:
                df.loc[idx, 'ANOMALY'] = True
                df.loc[idx, 'ANOMALY_SCORE'] += 1.5
                df.loc[idx, 'ANOMALY_REASON'] += \
                    f'First transaction in {row["CATEGORY"]} | '
            seen_categories.add(row['CATEGORY'])

    # ── Method 3: Velocity Check ──────────────────────────
    df_sorted = df.sort_values('DATE').copy()
    df_sorted['DATE'] = pd.to_datetime(df_sorted['DATE'])

    for account in df['Account No'].unique():
        acc_mask = df_sorted['Account No'] == account
        acc_df = df_sorted[acc_mask]

        daily_counts = acc_df.groupby(
            acc_df['DATE'].dt.date
        ).size()

        if len(daily_counts) > 3:
            mean_daily = daily_counts.mean()
            std_daily = daily_counts.std()

            if std_daily > 0:
                high_velocity_days = daily_counts[
                    daily_counts > mean_daily + sensitivity * std_daily
                ].index

                for day in high_velocity_days:
                    day_mask = (
                        (df['Account No'] == account) &
                        (pd.to_datetime(df['DATE']).dt.date == day)
                    )
                    df.loc[day_mask, 'ANOMALY'] = True
                    df.loc[day_mask, 'ANOMALY_SCORE'] += 2.0
                    df.loc[day_mask, 'ANOMALY_REASON'] += \
                        f'High velocity: {daily_counts[day]} transactions in one day | '

    # ── Method 4: Suspicious round numbers ───────────────
    round_mask = (
        (df['TYPE'] == 'DEBIT') &
        (df['AMOUNT'].abs() % 100000 == 0) &
        (df['AMOUNT'].abs() >= 100000)
    )
    df.loc[round_mask, 'ANOMALY'] = True
    df.loc[round_mask, 'ANOMALY_SCORE'] += 1.0
    df.loc[round_mask, 'ANOMALY_REASON'] += 'Suspicious round number | '

    # ── Risk level ────────────────────────────────────────
    df['RISK_LEVEL'] = 'Normal'
    df.loc[df['ANOMALY_SCORE'] > 0, 'RISK_LEVEL'] = 'Low Risk'
    df.loc[df['ANOMALY_SCORE'] > 2, 'RISK_LEVEL'] = 'Medium Risk'
    df.loc[df['ANOMALY_SCORE'] > 4, 'RISK_LEVEL'] = 'High Risk'

    # Clean up reason
    df['ANOMALY_REASON'] = df['ANOMALY_REASON'].str.rstrip(' | ')

    return df


def get_anomaly_summary(df_with_anomalies):
    anomalies = df_with_anomalies[df_with_anomalies['ANOMALY'] == True]

    total_anomalies = len(anomalies)
    high_risk = len(anomalies[anomalies['RISK_LEVEL'] == 'High Risk'])
    medium_risk = len(anomalies[anomalies['RISK_LEVEL'] == 'Medium Risk'])
    low_risk = len(anomalies[anomalies['RISK_LEVEL'] == 'Low Risk'])
    total_amount = anomalies['AMOUNT'].abs().sum()
    anomaly_rate = (total_anomalies / len(df_with_anomalies) * 100
                    if len(df_with_anomalies) > 0 else 0)

    summary = {
        'total_anomalies': total_anomalies,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'total_anomaly_amount': total_amount,
        'anomaly_rate': anomaly_rate
    }

    return summary