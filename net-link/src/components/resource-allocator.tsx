import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const ResourceAllocationDashboard = () => {
  const [clusters, setClusters] = useState([]);
  const [priorities, setPriorities] = useState([]);

  useEffect(() => {
    // Fetch data from Flask backend
    const fetchData = async () => {
      try {
        const clusterResponse = await fetch('/clusters');
        const priorityResponse = await fetch('/investment-priorities');
        
        const clusterData = await clusterResponse.json();
        const priorityData = await priorityResponse.json();

        setClusters(clusterData);
        setPriorities(priorityData);
      } catch (error) {
        console.error('Data fetch error:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      {/* Clusters Chart */}
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-bold mb-4">School Connectivity Clusters</h2>
        <LineChart width={500} height={300} data={clusters}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="cluster" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="connectivity_score.mean" stroke="#8884d8" />
        </LineChart>
      </div>

      {/* Investment Priorities Table */}
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-bold mb-4">Top Priority Schools</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th>School Name</th>
              <th>Country</th>
              <th>Priority Score</th>
            </tr>
          </thead>
          <tbody>
            {priorities.map((school, index) => (
              <tr key={index} className="border-b">
                <td>{school.school_name_x}</td>
                <td>{school.country_x}</td>
                <td>{school.investment_priority.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Geospatial Map */}
      <div className="col-span-2 bg-white shadow rounded-lg p-4">
        <h2 className="text-xl font-bold mb-4">School Locations</h2>
        <MapContainer center={[0, 0]} zoom={2} className="h-[500px]">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {priorities.map((school, index) => (
            <Marker 
              key={index} 
              position={[school.latitude, school.longitude]}
            >
              <Popup>
                {school.school_name_x}<br />
                Priority: {school.investment_priority.toFixed(2)}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default ResourceAllocationDashboard;