import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile
import os
import io
from datetime import datetime


# ── Color Palette ─────────────────────────────────────────
PRIMARY = colors.HexColor('#2C3E50')
ACCENT = colors.HexColor('#3498DB')
GREEN = colors.HexColor('#2ECC71')
RED = colors.HexColor('#E74C3C')
ORANGE = colors.HexColor('#F39C12')
LIGHT_GRAY = colors.HexColor('#F8F9FA')
BORDER = colors.HexColor('#DEE2E6')


def save_plotly_as_image(fig, width=700, height=400):
    """Save Plotly figure as PNG bytes"""
    img_bytes = fig.to_image(format='png', width=width, height=height, scale=2)
    return img_bytes


def build_spending_pie(filtered_df):
    """Build spending pie chart"""
    debit_by_cat = (
        filtered_df[filtered_df['TYPE'] == 'DEBIT']
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.pie(
        debit_by_cat,
        values='AMOUNT',
        names='CATEGORY',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title='Spending by Category'
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=12)
    )
    return fig


def build_monthly_trend(filtered_df, currency):
    """Build monthly trend chart"""
    filtered_df = filtered_df.copy()
    filtered_df['MONTH'] = filtered_df['DATE'].dt.to_period('M').astype(str)

    monthly_flow = filtered_df.groupby(
        ['MONTH', 'TYPE']
    )['AMOUNT'].sum().abs().reset_index()
    monthly_flow.columns = ['MONTH', 'TYPE', 'AMOUNT']

    fig = px.bar(
        monthly_flow,
        x='MONTH',
        y='AMOUNT',
        color='TYPE',
        barmode='group',
        color_discrete_map={
            'CREDIT': '#2ECC71',
            'DEBIT': '#E74C3C'
        },
        title=f'Income vs Expenses by Month ({currency})'
    )
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis_tickangle=45,
        font=dict(size=11)
    )
    return fig


def generate_pdf_report(
    filtered_df,
    total_income,
    total_spent,
    net_balance,
    total_tx,
    currency,
    data_source,
    selected_account,
    ai_insights,
    budgets=None,
    anomaly_summary=None
):
    """Generate complete PDF financial report"""

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom Styles ──────────────────────────────────────
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.gray,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=PRIMARY,
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        borderPad=4
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=6,
        leading=16
    )

    # ── HEADER ────────────────────────────────────────────
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("💰 Personal Finance Report", title_style))

    market = "Kazakhstan 🇰🇿" if '🇰🇿' in data_source else "India 🇮🇳"
    report_date = datetime.now().strftime("%B %d, %Y")

    story.append(Paragraph(
        f"Account: {selected_account} | Market: {market} | Generated: {report_date}",
        subtitle_style
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=ACCENT,
        spaceAfter=20
    ))

    # ── KPI SUMMARY TABLE ─────────────────────────────────
    story.append(Paragraph("📊 Financial Summary", section_style))

    savings_rate = (
        (total_income - total_spent) / total_income * 100
        if total_income > 0 else 0
    )

    kpi_data = [
        ['Metric', 'Value', 'Status'],
        [
            'Total Income',
            f"{currency}{total_income:,.0f}",
            '✅ Good'
        ],
        [
            'Total Spent',
            f"{currency}{total_spent:,.0f}",
            '🔴 High' if total_spent > total_income else '✅ Normal'
        ],
        [
            'Net Balance',
            f"{currency}{net_balance:,.0f}",
            '✅ Positive' if net_balance > 0 else '🔴 Negative'
        ],
        [
            'Savings Rate',
            f"{savings_rate:.1f}%",
            '✅ Healthy' if savings_rate >= 20 else
            '🟡 Low' if savings_rate >= 10 else '🔴 Critical'
        ],
        [
            'Total Transactions',
            f"{total_tx:,}",
            '📊 Tracked'
        ],
    ]

    kpi_table = Table(kpi_data, colWidths=[6*cm, 5*cm, 5*cm])
    kpi_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Body
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))

    story.append(kpi_table)
    story.append(Spacer(1, 0.3*inch))

    # ── SPENDING PIE CHART ────────────────────────────────
    story.append(Paragraph("📊 Spending by Category", section_style))

    try:
        pie_fig = build_spending_pie(filtered_df)
        pie_bytes = save_plotly_as_image(pie_fig, width=600, height=380)
        pie_img = Image(io.BytesIO(pie_bytes), width=14*cm, height=9*cm)
        pie_img.hAlign = 'CENTER'
        story.append(pie_img)
    except Exception as e:
        story.append(Paragraph(f"Chart unavailable: {str(e)}", body_style))

    story.append(Spacer(1, 0.2*inch))

    # ── MONTHLY TREND CHART ───────────────────────────────
    story.append(Paragraph("📈 Monthly Income vs Expenses", section_style))

    try:
        trend_fig = build_monthly_trend(filtered_df, currency)
        trend_bytes = save_plotly_as_image(trend_fig, width=600, height=350)
        trend_img = Image(io.BytesIO(trend_bytes), width=15*cm, height=9*cm)
        trend_img.hAlign = 'CENTER'
        story.append(trend_img)
    except Exception as e:
        story.append(Paragraph(f"Chart unavailable: {str(e)}", body_style))

    story.append(Spacer(1, 0.2*inch))

    # ── CATEGORY BREAKDOWN TABLE ──────────────────────────
    story.append(Paragraph("📋 Spending Breakdown by Category", section_style))

    EXCLUDE = ['Transfer', 'ATM & Cash', 'Other']
    real_spending = filtered_df[
        (filtered_df['TYPE'] == 'DEBIT') &
        (~filtered_df['CATEGORY'].isin(EXCLUDE))
    ]

    cat_summary = (
        real_spending
        .groupby('CATEGORY')['AMOUNT']
        .agg(['sum', 'count'])
        .abs()
        .round(0)
        .reset_index()
        .sort_values('sum', ascending=False)
    )
    cat_summary.columns = ['Category', 'Total Spent', 'Transactions']

    cat_data = [['Category', 'Total Spent', 'Transactions', '% of Total']]
    total_real = cat_summary['Total Spent'].sum()

    for _, row in cat_summary.iterrows():
        pct = (row['Total Spent'] / total_real * 100) if total_real > 0 else 0
        cat_data.append([
            row['Category'],
            f"{currency}{row['Total Spent']:,.0f}",
            str(int(row['Transactions'])),
            f"{pct:.1f}%"
        ])

    cat_table = Table(
        cat_data,
        colWidths=[6*cm, 4.5*cm, 3.5*cm, 3*cm]
    )
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(cat_table)
    story.append(Spacer(1, 0.3*inch))

    # ── BUDGET STATUS ─────────────────────────────────────
    if budgets:
        story.append(Paragraph("🎯 Budget Status", section_style))

        budget_data = [['Category', 'Budget', 'Actual', 'Remaining', 'Status']]

        for category, budget_limit in budgets.items():
            actual = real_spending[
                real_spending['CATEGORY'] == category
            ]['AMOUNT'].abs().sum()

            remaining = budget_limit - actual
            pct = (actual / budget_limit * 100) if budget_limit > 0 else 0
            status = (
                'Over Budget' if pct > 100 else
                'Warning' if pct > 80 else
                'On Track'
            )

            budget_data.append([
                category,
                f"{currency}{budget_limit:,.0f}",
                f"{currency}{actual:,.0f}",
                f"{currency}{remaining:,.0f}",
                status
            ])

        budget_table = Table(
            budget_data,
            colWidths=[5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 2.5*cm]
        )
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(budget_table)
        story.append(Spacer(1, 0.3*inch))

    # ── ANOMALY SUMMARY ───────────────────────────────────
    if anomaly_summary:
        story.append(Paragraph("🚨 Anomaly Detection Summary", section_style))

        anomaly_data = [
            ['Metric', 'Count'],
            ['Total Flagged Transactions',
             str(anomaly_summary.get('total_anomalies', 0))],
            ['High Risk', str(anomaly_summary.get('high_risk', 0))],
            ['Medium Risk', str(anomaly_summary.get('medium_risk', 0))],
            ['Low Risk', str(anomaly_summary.get('low_risk', 0))],
            ['Anomaly Rate',
             f"{anomaly_summary.get('anomaly_rate', 0):.1f}%"],
            ['Total Amount in Flagged Transactions',
             f"{currency}{anomaly_summary.get('total_anomaly_amount', 0):,.0f}"],
        ]

        anomaly_table = Table(anomaly_data, colWidths=[10*cm, 7*cm])
        anomaly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), RED),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, colors.white]),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(anomaly_table)
        story.append(Spacer(1, 0.3*inch))

    # ── AI INSIGHTS ───────────────────────────────────────
    if ai_insights:
        story.append(Paragraph("🤖 AI Financial Advisor Insights", section_style))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=ACCENT,
            spaceAfter=10
        ))

        # Clean markdown for PDF
        clean_insights = (
            ai_insights
            .replace('**', '')
            .replace('##', '')
            .replace('#', '')
            .replace('*', '•')
        )

        for line in clean_insights.split('\n'):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))

        story.append(Spacer(1, 0.2*inch))

    # ── FOOTER ────────────────────────────────────────────
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=BORDER,
        spaceBefore=20,
        spaceAfter=10
    ))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )

    story.append(Paragraph(
        f"Generated by PFM AI Assistant | {report_date} | "
        f"Powered by Llama 3 & Prophet ML",
        footer_style
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()