import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class ResourceAllocationOptimizer:
    def __init__(self, data):
        self.data = data
        self.preprocess_data()
    
    def preprocess_data(self):
        # Clean and prepare data for analysis
        self.data['connectivity_score'] = (
            self.data['connection_quality_score'] * 
            self.data['normalized_quality_score']
        )
        
        # Select key features for optimization
        self.features = [
            'latitude', 'longitude', 
            'connectivity_score', 
            'distance_to_server'
        ]
        
        # Normalize features
        self.scaler = StandardScaler()
        self.scaled_features = self.scaler.fit_transform(
            self.data[self.features]
        )
    
    def cluster_schools(self, n_clusters=5):
        # Perform clustering to identify school groups
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.data['cluster'] = kmeans.fit_predict(self.scaled_features)
        
        # Analyze cluster characteristics
        cluster_summary = self.data.groupby('cluster').agg({
            'connectivity_score': ['mean', 'count'],
            'distance_to_server': 'mean',
            'school_name_x': 'count'
        }).reset_index()
        
        return cluster_summary
    
    def prioritize_investments(self):
        # Rank schools for potential resource allocation
        self.data['investment_priority'] = (
            (1 / self.data['connectivity_score']) * 
            self.data['distance_to_server']
        )
        
        top_priority_schools = self.data.nlargest(
            10, 'investment_priority'
        )[['school_name_x', 'country_x', 'investment_priority']]
        
        return top_priority_schools.to_dict(orient='records')
