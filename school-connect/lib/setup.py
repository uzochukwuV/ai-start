import pandas as pd
import numpy as np
import geopy.distance
from geopy.geocoders import Nominatim
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from geopy.distance import geodesic

class BandwidthResourceAnalyzer:
    def __init__(self, data):
        # Load and merge datasets
       
        self.merged_df = data
    
    def calculate_connection_quality_score(self, data):
        """
        Enhanced connection quality scoring with multiple factors
        """
        # Normalize score to 0-100 range
        scaler = MinMaxScaler(feature_range=(0, 100))
        data['normalized_quality_score'] = scaler.fit_transform(
            data[['connection_quality_score']]
        )
        
        return data
    
    def geographic_clustering(self, n_clusters=5):
        """
        Cluster schools based on geographic proximity and connectivity
        """
        coordinates = self.merged_df[['latitude', 'longitude']].values
        quality_scores = self.merged_df['normalized_quality_score'].values
        
        # Combined features for clustering
        clustering_features = np.column_stack([
            coordinates, 
            quality_scores.reshape(-1, 1)
        ])
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.merged_df['connectivity_cluster'] = kmeans.fit_predict(clustering_features)
        
        return self.merged_df
    def predict_connection_quality(self,latitude, longitude, cluster_label):
        # Find schools in the same cluster
        cluster_schools = self.merged_df[self.merged_df['connectivity_cluster'] == cluster_label]

        # Calculate the average connection quality score for schools in that cluster
        predicted_quality = cluster_schools['connection_quality_score'].mean()
        return predicted_quality

    def predict_connection_quality_weighted(self , latitude, longitude, cluster_label):
        cluster_schools = self.merged_df[self.merged_df['connectivity_cluster'] == cluster_label]
        total_weighted_quality = 0
        total_weights = 0
        for index, row in cluster_schools.iterrows():
            distance = geodesic((latitude, longitude), (row['latitude'], row['longitude'])).km
            if distance > 0: # avoid division by zero
                weight = 1 / distance
                total_weighted_quality += row['connection_quality_score'] * weight
                total_weights += weight
            
        if total_weights > 0:
            predicted_quality = total_weighted_quality / total_weights
        else:
            predicted_quality = cluster_schools['connection_quality_score'].mean() # Fallback to simple average
        return predicted_quality
        
    def forecast_connectivity(self):
        """
        Multiple time series forecasting methods
        """
        df_forecast = self.merged_df[['normalized_quality_score']].copy()
        df_forecast['ds'] = pd.to_datetime(self.merged_df['date'])
        df_forecast = df_forecast.rename(columns={'normalized_quality_score': 'y'})
        
        # ARIMA Forecast
        arima_model = ARIMA(df_forecast['y'], order=(5, 1, 0))
        arima_results = arima_model.fit()
        arima_forecast = arima_results.forecast(steps=7)
        
        # Prophet Forecast
        prophet_model = Prophet()
        prophet_model.fit(df_forecast)
        future = prophet_model.make_future_dataframe(periods=7)
        prophet_forecast = prophet_model.predict(future)
        
        return {
            'arima_forecast': arima_forecast,
            'prophet_forecast': prophet_forecast
        }
    
    def recommend_resource_allocation(self):
        """
        Generate recommendations based on connectivity clusters
        """
        cluster_summary = self.merged_df.groupby('connectivity_cluster').agg({
            'normalized_quality_score': ['mean', 'min', 'max'],
            'school_id_giga': 'count'
        })
        
        recommendations = []
        for cluster, stats in cluster_summary.iterrows():
            recommendation = {
                'cluster': cluster,
                'avg_quality_score': stats[('normalized_quality_score', 'mean')],
                'schools_count': stats[('school_id_giga', 'count')],
                'priority': 'High' if stats[('normalized_quality_score', 'mean')] < 40 else 'Medium'
            }
            recommendations.append(recommendation)
        
        return recommendations

def main():
    analyzer = BandwidthResourceAnalyzer(
        'school_geolocation.csv', 
        'measurements.csv'
    )
    
    # Calculate connection quality
    quality_df = analyzer.calculate_connection_quality_score()
    
    # Perform geographic clustering
    clustered_df = analyzer.geographic_clustering()
    
    # Forecast connectivity
    forecasts = analyzer.forecast_connectivity()
    
    # Get resource allocation recommendations
    recommendations = analyzer.recommend_resource_allocation()
    
    return {
        'quality_dataframe': quality_df,
        'clustered_dataframe': clustered_df,
        'forecasts': forecasts,
        'recommendations': recommendations
    }

