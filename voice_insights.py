import streamlit as st
from groq import Groq
import os
import tempfile

def transcribe_audio(audio_bytes, client):
    """Transcribe audio using Whisper via Groq"""
    try:
        with tempfile.NamedTemporaryFile(
            suffix='.wav', delete=False
        ) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        with open(tmp_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_file.read()),
                model="whisper-large-v3",
                prompt="This is a question about personal finances, bank transactions, spending categories.",
                language="ru"
            )
        
        os.unlink(tmp_path)
        return transcription.text
    
    except Exception as e:
        return f"Transcription error: {str(e)}"

def answer_finance_question(
    question, filtered_df, budgets,
    currency, data_source, client
):
    """Answer voice question using spending data"""
    
    # Build context from current dashboard data
    total_income = filtered_df[
        filtered_df['TYPE'] == 'CREDIT'
    ]['AMOUNT'].sum()
    
    total_spent = abs(
        filtered_df[filtered_df['TYPE'] == 'DEBIT']['AMOUNT'].sum()
    )
    
    net_balance = total_income - total_spent
    
    # Spending by category
    EXCLUDE = ['Transfer', 'ATM & Cash', 'Other']
    real_spending = filtered_df[
        (filtered_df['TYPE'] == 'DEBIT') &
        (~filtered_df['CATEGORY'].isin(EXCLUDE))
    ]
    
    cat_summary = (
        real_spending
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    
    # Top merchants
    top_merchants = (
        real_spending
        .groupby('TRANSACTION DETAILS')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    
    # Budget context
    budget_context = ""
    if budgets:
        budget_context = "\nBUDGET LIMITS SET BY USER:\n"
        for cat, limit in budgets.items():
            budget_context += f"  {cat}: {currency}{limit:,.0f}/month\n"
    
    # Market context
    if '🇰🇿' in data_source:
        market = "Kazakhstan (Tenge ₸)"
        banks = "Kaspi Bank, Halyk Bank, Freedom Bank"
    else:
        market = "India (Rupee ₹)"
        banks = "SBI, HDFC, ICICI"
    
    system_prompt = f"""You are a voice-based personal finance assistant for {market}.
Answer questions about the user's bank transactions concisely.
Speak naturally — your response will be read aloud.
No bullet points or markdown — just natural speech.
Keep answers under 3 sentences.
Currency: {currency}
Local banks: {banks}

CURRENT FINANCIAL DATA:
- Total Income: {currency}{total_income:,.0f}
- Total Spent: {currency}{total_spent:,.0f}  
- Net Balance: {currency}{net_balance:,.0f}
- Savings Rate: {((net_balance/total_income)*100) if total_income > 0 else 0:.1f}%

SPENDING BY CATEGORY:
{cat_summary.to_string(index=False)}

TOP 5 MERCHANTS:
{top_merchants.to_string(index=False)}
{budget_context}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        max_tokens=200
    )
    
    return response.choices[0].message.content

def text_to_speech(text, client):
    """Convert text to speech using gTTS"""
    try:
        from gtts import gTTS
        import tempfile
        import base64
        
        tts = gTTS(text=text, lang='ru', slow=False)
        
        with tempfile.NamedTemporaryFile(
            suffix='.mp3', delete=False
        ) as tmp_file:
            tts.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        with open(tmp_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        os.unlink(tmp_path)
        return audio_bytes
    
    except Exception as e:
        return None