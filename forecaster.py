import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

def prepare_forecast_data(filtered_df, category=None):
    """Prepare monthly spending data for Prophet"""
    
    df = filtered_df[filtered_df['TYPE'] == 'DEBIT'].copy()
    
    # Filter by category if specified
    if category and category != 'All Categories':
        df = df[df['CATEGORY'] == category]
    
    # Exclude transfers and ATM
    EXCLUDE = ['Transfer', 'ATM & Cash', 'Other']
    df = df[~df['CATEGORY'].isin(EXCLUDE)]
    
    # Group by month
    df['MONTH'] = df['DATE'].dt.to_period('M').dt.to_timestamp()
    monthly = (
        df.groupby('MONTH')['AMOUNT']
        .sum()
        .abs()
        .reset_index()
    )
    monthly.columns = ['ds', 'y']
    
    return monthly

def run_forecast(monthly_data, periods=3):
    """Run Prophet forecast"""
    
    if len(monthly_data) < 3:
        return None, None
    
    # Initialize Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        interval_width=0.80
    )
    
    # Fit model
    model.fit(monthly_data)
    
    # Create future dataframe
    future = model.make_future_dataframe(
        periods=periods,
        freq='MS'  # Month Start
    )
    
    # Predict
    forecast = model.predict(future)
    
    return model, forecast

def build_forecast_chart(monthly_data, forecast, currency='₸'):
    """Build Plotly chart with actual + forecast"""
    
    # Split into actual and future
    last_actual_date = monthly_data['ds'].max()
    
    forecast_future = forecast[forecast['ds'] > last_actual_date]
    forecast_actual = forecast[forecast['ds'] <= last_actual_date]
    
    fig = go.Figure()
    
    # Actual spending bars
    fig.add_trace(go.Bar(
        x=monthly_data['ds'],
        y=monthly_data['y'],
        name='Actual Spending',
        marker_color='#3498DB',
        opacity=0.8
    ))
    
    # Forecast bars
    fig.add_trace(go.Bar(
        x=forecast_future['ds'],
        y=forecast_future['yhat'].clip(lower=0),
        name='Forecasted Spending',
        marker_color='#E74C3C',
        opacity=0.8
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_future['ds'],
                     forecast_future['ds'].iloc[::-1]]),
        y=pd.concat([forecast_future['yhat_upper'].clip(lower=0),
                     forecast_future['yhat_lower'].clip(lower=0).iloc[::-1]]),
        fill='toself',
        fillcolor='rgba(231,76,60,0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval (80%)',
        showlegend=True
    ))
    
    # Trend line
    fig.add_trace(go.Scatter(
        x=forecast_actual['ds'],
        y=forecast_actual['yhat'].clip(lower=0),
        mode='lines',
        name='Trend',
        line=dict(color='#F39C12', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title='📈 Spending Forecast — Next 3 Months',
        xaxis_title='Month',
        yaxis_title=f'Amount ({currency})',
        barmode='overlay',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def get_forecast_insights(monthly_data, forecast, currency='₸'):
    """Generate key forecast metrics"""
    
    last_actual_date = monthly_data['ds'].max()
    forecast_future = forecast[forecast['ds'] > last_actual_date]
    
    if forecast_future.empty:
        return {}
    
    avg_actual = monthly_data['y'].mean()
    next_month = forecast_future.iloc[0]
    next_month_pred = max(0, next_month['yhat'])
    
    pct_change = ((next_month_pred - avg_actual) / avg_actual * 100
                  if avg_actual > 0 else 0)
    
    insights = {
        'next_month_date': next_month['ds'].strftime('%B %Y'),
        'next_month_predicted': next_month_pred,
        'next_month_lower': max(0, next_month['yhat_lower']),
        'next_month_upper': max(0, next_month['yhat_upper']),
        'avg_actual': avg_actual,
        'pct_change': pct_change,
        'trend': 'increasing' if pct_change > 5 else
                 'decreasing' if pct_change < -5 else 'stable'
    }
    
    return insights