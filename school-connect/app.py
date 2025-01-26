
from lib.setup import BandwidthResourceAnalyzer
from flask import Flask, jsonify, request
import os
import pandas as pd
import numpy as np
from flask import Flask, jsonify, render_template

import statsmodels.tsa.arima.model as ARIMA
from prophet import Prophet
import json
from flask_cors import CORS, cross_origin
from lib.resource_allocator import ResourceAllocationOptimizer
from geopy.geocoders import Nominatim
from lib.util import *
from sklearn.impute import SimpleImputer

BASE_DIR = os.getcwd()

app = Flask(__name__)
CORS(app,resources={r"/*": {"origins": ["https://ominous-acorn-rx4vvjv44v9fxp9-5173.app.github.dev/", "http://localhost:*"]}})

school_location = os.path.join(BASE_DIR, "data/school_geolocation.csv")
school_messurement = os.path.join(BASE_DIR, "data/measurements.csv")

# Load and preprocess data
school_location_df =  pd.read_csv(school_location)
school_measurement_df = pd.read_csv(school_messurement)
merged_df = pd.merge(school_location_df, school_measurement_df, on='school_id_giga', how='inner').head(500)


# Calculate connection quality score
merged_df['connection_quality_score'] = (
    (merged_df['download_speed'] + merged_df['upload_speed']) / 2
    * (1 / (merged_df['latency'] + 1))
)


df = merged_df.groupby('school_id_giga').agg(
    {
        'school_name_x': 'first',  # Take the first school name
        'latitude': 'first',  # Take the first latitude (assuming it's consistent)
        'longitude': 'first',  # Take the first longitude
        'download_speed': 'mean',
        'upload_speed': 'mean',
        'latency': 'mean',
        'connection_quality_score': 'mean',
        'date': 'first',
        'server_location':'first',
        'country_x':'first',
        'iso2_code':'first',
        'education_level':'first',
        'iso2_code':'first',
        'iso3_code':'first',
    }
).reset_index()

df['server_location_latitude'], df['server_location_longitude'] = df['server_location'].apply(lambda x: get_coordinates(x)[0]),  df.head(5)['server_location'].apply(lambda x: get_coordinates(x)[1])

savejson()
df['server_location_latitude'].fillna(1, inplace=True)
df['server_location_longitude'].fillna(1, inplace=True)


school_performance = merged_df.groupby('school_id_giga')['connection_quality_score'].agg(['mean', 'median', 'std', 'min', 'max'])

schools = df.sort_values(by='connection_quality_score', ascending=False)

school_performance = pd.merge(school_performance,df[['school_id_giga', 'school_name_x']], on='school_id_giga', how='left')
# Sort schools by mean connection quality score in descending order
school_performance = school_performance.sort_values('mean', ascending=False)


df['distance_to_server'] = df.apply(calculate_distance, axis=1)
df['distance_to_server'].fillna(1, inplace=True)

imp = SimpleImputer(strategy="most_frequent")
print(imp.fit_transform(df))

bandwidth = BandwidthResourceAnalyzer(df)
bandwidth.calculate_connection_quality_score(df)

optimizer = ResourceAllocationOptimizer(df)



@app.route('/clusters', methods=['GET'])
def get_clusters():
    optimizer.preprocess_data()
    clusters = optimizer.cluster_schools()
    return jsonify(clusters.to_dict(orient='records'))

@app.route('/investment-priorities', methods=['GET'])
def get_investment_priorities():
    priorities = optimizer.prioritize_investments()
    return jsonify(priorities)

@app.route('/optimize',  methods=['GET'])
def optimize_resources():
    # Additional customization logic can be added here
    clusters = optimizer.cluster_schools(
        n_clusters=5
    )
    priorities = optimizer.prioritize_investments()
    
    return jsonify({
        'clusters': clusters.to_dict(orient='records'),
        'priorities': priorities
    })


@app.route('/')
def index():
    """Main dashboard route"""
    return render_template('index.html')



@app.route('/top_schools')
@cross_origin()
def get_top_schools():
    """
    Returns a JSON of the top 5 performing schools.
    """
    top_schools = schools[['school_name_x', 'connection_quality_score', "school_id_giga"]].head(10)
    return jsonify(top_schools.to_dict(orient='index'))

@app.route('/bottom_schools')
@cross_origin()
def get_bottom_schools():
    """
    Returns a JSON of the bottom 5 performing schools.
    """
    bottom_schools = schools[['school_name_x', 'connection_quality_score', "school_id_giga"]].head(10)
    return jsonify(bottom_schools.to_dict(orient='index'))


@app.route('/school_comparison')
@cross_origin()
def get_school_comparison():
    """
    Returns a JSON of all schools and their performance metrics.
    """
    return jsonify(school_performance.head(10).to_dict(orient='index'))

@app.route('/real-time-monitoring')
def real_time_monitoring():
    """Return current network performance metrics"""
    historical_data = merged_df[['school_id_giga', 'school_name_x', 'date', 'download_speed', 'upload_speed', 'latency', 'connection_quality_score']]
    data = historical_data.head(20).to_dict()
    return jsonify(data)

@app.route('/historical-performance')
def historical_performance():
    """Return historical network performance data"""
    school_performance = merged_df.groupby('school_name')['connection_quality_score'].agg(['mean', 'median', 'std', 'min', 'max'])
    return school_performance.to_json(orient='index')

@app.route('/predictive-forecast')
def predictive_forecast():
    """Generate network performance forecasts"""
    df_forecast = merged_df[['connection_quality_score', 'date']].copy()
    df_forecast.rename(columns={'connection_quality_score': 'y', 'date': 'ds'}, inplace=True)
    
    try:
        # Prophet forecast
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        return jsonify({
            'forecast_dates': forecast['ds'].tolist(),
            'forecast_values': forecast['yhat'].tolist(),
            'lower_bound': forecast['yhat_lower'].tolist(),
            'upper_bound': forecast['yhat_upper'].tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/performance-comparison')
def performance_comparison():
    """Compare network performance across schools"""
    school_performance = merged_df.groupby('school_name')['connection_quality_score'].agg(['mean', 'median'])
    return school_performance.to_json(orient='index')

@app.route('/server-distance-analysis')
def server_distance_analysis():
    """Analyze relationship between server distance and network performance"""
    # Calculate correlation between distance and connection quality
    correlation = merged_df[['distance_to_server', 'connection_quality_score']].corr().iloc[0, 1]
    
    return jsonify({
        'correlation': correlation,
        'school_distances': merged_df[['school_name', 'distance_to_server', 'connection_quality_score']].to_dict(orient='records')
    })

@app.route('/geolocation-data')
def geolocation_data():
    """Return geolocation data for mapping"""
    geo_data = merged_df[['school_name', 'latitude', 'longitude', 'connection_quality_score']]
    return geo_data.to_json(orient='records')

@app.route('/automated-report')
def automated_report():
    """Generate a comprehensive network performance report"""
    # Aggregate performance metrics
    overall_metrics = {
        'total_schools': len(merged_df),
        'avg_connection_quality': merged_df['connection_quality_score'].mean(),
        'median_connection_quality': merged_df['connection_quality_score'].median(),
        'top_performing_schools': merged_df.nlargest(5, 'connection_quality_score')[['school_name', 'connection_quality_score']].to_dict(orient='records'),
        'bottom_performing_schools': merged_df.nsmallest(5, 'connection_quality_score')[['school_name', 'connection_quality_score']].to_dict(orient='records')
    }
    
    return jsonify(overall_metrics)







# Apply the function to get coordinates for each country



if __name__ == '__main__':
    app.run(debug=True)