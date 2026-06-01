import pandas as pd
import asyncio
import schedule
import time
import os
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)


def load_transactions(filepath='kz_transactions.csv'):
    """Load transaction data"""
    df = pd.read_csv(filepath, parse_dates=['DATE'])
    return df


def get_weekly_summary(df, account_no=None):
    """Get last 7 days spending summary"""

    # Filter last 7 days
    end_date = df['DATE'].max()
    start_date = end_date - timedelta(days=7)

    weekly = df[
        (df['DATE'] >= start_date) &
        (df['DATE'] <= end_date)
    ].copy()

    if account_no:
        weekly = weekly[weekly['Account No'] == account_no]

    # Key metrics
    income = weekly[weekly['TYPE'] == 'CREDIT']['AMOUNT'].sum()
    spent = abs(weekly[weekly['TYPE'] == 'DEBIT']['AMOUNT'].sum())
    net = income - spent
    tx_count = len(weekly)

    # Spending by category
    EXCLUDE = ['Transfer', 'ATM & Cash', 'Other']
    real_spending = weekly[
        (weekly['TYPE'] == 'DEBIT') &
        (~weekly['CATEGORY'].isin(EXCLUDE))
    ]

    cat_summary = (
        real_spending
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    # Top merchant
    top_merchant = (
        real_spending
        .groupby('TRANSACTION DETAILS')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )

    return {
        'income': income,
        'spent': spent,
        'net': net,
        'tx_count': tx_count,
        'start_date': start_date.strftime('%d %b'),
        'end_date': end_date.strftime('%d %b %Y'),
        'cat_summary': cat_summary,
        'top_merchant': top_merchant
    }


def generate_ai_summary(summary, currency='₸'):
    """Generate AI weekly summary using Llama 3"""

    cat_text = '\n'.join([
        f"  • {row['CATEGORY']}: {currency}{row['AMOUNT']:,.0f}"
        for _, row in summary['cat_summary'].iterrows()
    ])

    merchant_text = '\n'.join([
        f"  • {row['TRANSACTION DETAILS']}: {currency}{row['AMOUNT']:,.0f}"
        for _, row in summary['top_merchant'].iterrows()
    ])

    prompt = f"""Weekly financial report for Kazakhstan bank customer.
Period: {summary['start_date']} — {summary['end_date']}

Income: {currency}{summary['income']:,.0f}
Spent: {currency}{summary['spent']:,.0f}
Net: {currency}{summary['net']:,.0f}
Transactions: {summary['tx_count']}

Top spending categories:
{cat_text}

Top merchants:
{merchant_text}

Write a very short weekly summary (3-4 sentences max).
Include one key insight and one actionable tip.
Write in a friendly conversational tone.
No markdown symbols."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly personal finance assistant. Write brief, encouraging weekly summaries."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=200
    )

    return response.choices[0].message.content


def format_telegram_message(summary, ai_insight, currency='₸'):
    """Format beautiful Telegram message"""

    # Status emoji for net balance
    net_emoji = '✅' if summary['net'] >= 0 else '🔴'
    savings_rate = (
        (summary['net'] / summary['income'] * 100)
        if summary['income'] > 0 else 0
    )

    # Category breakdown
    cat_lines = '\n'.join([
        f"  {'🔴' if i == 0 else '🟡' if i == 1 else '🔵'} "
        f"{row['CATEGORY']}: `{currency}{row['AMOUNT']:,.0f}`"
        for i, (_, row) in enumerate(summary['cat_summary'].iterrows())
    ])

    # Top merchants
    merchant_lines = '\n'.join([
        f"  • {row['TRANSACTION DETAILS'][:25]}: "
        f"`{currency}{row['AMOUNT']:,.0f}`"
        for _, row in summary['top_merchant'].iterrows()
    ])

    message = f"""💰 *Weekly Financial Report*
📅 {summary['start_date']} — {summary['end_date']}

━━━━━━━━━━━━━━━━━━━━
📊 *Summary*
💵 Income: `{currency}{summary['income']:,.0f}`
💸 Spent: `{currency}{summary['spent']:,.0f}`
{net_emoji} Net: `{currency}{summary['net']:,.0f}`
💾 Savings Rate: `{savings_rate:.1f}%`
🔢 Transactions: `{summary['tx_count']}`

━━━━━━━━━━━━━━━━━━━━
🏷️ *Top Spending Categories*
{cat_lines}

━━━━━━━━━━━━━━━━━━━━
🏪 *Top Merchants*
{merchant_lines}

━━━━━━━━━━━━━━━━━━━━
🤖 *AI Insight*
_{ai_insight}_

━━━━━━━━━━━━━━━━━━━━
_Powered by PFM AI Assistant 🇰🇿_"""

    return message


async def send_weekly_report(currency='₸'):
    """Send weekly report to Telegram"""

    print(f"[{datetime.now()}] Generating weekly report...")

    try:
        # Load data
        df = load_transactions()

        # Get accounts
        accounts = df['Account No'].unique()

        bot = Bot(token=TELEGRAM_TOKEN)

        for account in accounts:
            # Get summary
            summary = get_weekly_summary(df, account_no=account)

            if summary['tx_count'] == 0:
                continue

            # Generate AI insight
            ai_insight = generate_ai_summary(summary, currency)

            # Format message
            message = format_telegram_message(
                summary, ai_insight, currency
            )

            # Send message
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )

            print(f"Report sent for account {account}")

        print("Weekly reports sent successfully!")

    except Exception as e:
        print(f"Error sending report: {e}")


async def send_test_message():
    """Send a test message to verify bot works"""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text="✅ *PFM AI Assistant Bot is connected!*\n\nYou will receive weekly spending reports every Monday at 9:00 AM 🇰🇿",
        parse_mode=ParseMode.MARKDOWN
    )
    print("Test message sent!")


def run_scheduler():
    """Run weekly scheduler"""

    print("Starting PFM Telegram Bot scheduler...")
    print("Weekly reports scheduled for every Monday at 9:00 AM")

    # Schedule weekly report — every Monday at 9:00 AM
    schedule.every().monday.at("09:00").do(
        lambda: asyncio.run(send_weekly_report())
    )

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Send test message
            asyncio.run(send_test_message())
        elif sys.argv[1] == "now":
            # Send report immediately
            asyncio.run(send_weekly_report())
        elif sys.argv[1] == "schedule":
            # Start scheduler
            run_scheduler()
    else:
        # Default — send test
        asyncio.run(send_test_message())