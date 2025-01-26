import React, { useState, useMemo, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  SearchIcon, 
  ChevronUpIcon, 
  ChevronDownIcon, 
  LucidePersonStanding
} from 'lucide-react';
import axios from 'axios';

type PerformanceDta = {
    name: {
        max: number;
        mean: number;
        median: number;
        min: number;
        std: number;
    }
}

// Performance data (replace with your full dataset)
const performanceData  = {
  "Centar za odgoj, obrazovanje i rehabilitaciju \"Vladimir Nazor\"": {
    "max": 20.955,
    "mean": 9.326,
    "median": 9.038,
    "min": 0.013,
    "std": 3.532
  },
  "JAVNA USTANOVA OSNOVNA ŠKOLA \"ARNAUTI\" ARNAUTI": {
    "max": 9.658,
    "mean": 7.115,
    "median": 7.192,
    "min": 0.006,
    "std": 1.414
  },
  // ... other schools from your dataset
};

type g = {
  string: {
    school_name_x?:string
    max: number;
    mean: number;
    min: number;
    std: number;
    median: number;
  }
}

type ConfigKey ={
    key:any;
    direction: any;
}

const SchoolPerformanceDashboard = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<ConfigKey>({ 
    key: 'mean', 
    direction: 'descending' 
  });
  const [data, setData] = useState(null);
  const [isloading, setLoading] = useState<boolean>(false);

  useEffect(()=>{
    if(data) return
    const fetchData = async () => {
        setLoading(true)
        try {
            axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
            axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
          const response = await fetch('https://ominous-acorn-rx4vvjv44v9fxp9-5000.app.github.dev/school_comparison', {
            method: 'GET',
            mode:"cors",
            headers: {
                'Access-Control-Allow-Origin': '*',
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
        }); // Replace with your API endpoint
         const res_data = await response.json()
         
         setData(res_data)
         
         setLoading(false)
        } catch (error) {
          console.error('Error fetching data:', error);
          setLoading(false)
        }
      };
  
      fetchData();
  }, [data])

 

  // Transform data for chart
  const chartData = useMemo(() => {
    if (data) return Object.entries(data!)
      .map(([school, metrics]) => {
        console.log(metrics)
        return {
          name: metrics.school_name_x,
          mean: metrics.mean,
          max: metrics.max,
          std: metrics.std
        }
      })
      .filter(school => 
        school.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
  }, [searchTerm, sortConfig, data]);

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'descending' 
        ? 'ascending' 
        : 'descending'
    }));
  };

   if(!data) return "Loading ........."
   console.log(chartData)
  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          School Network Performance Dashboard
          {isloading && <LucidePersonStanding />}
        </h1>

        {/* Search and Filter Section */}
        <div className="mb-6 flex items-center space-x-4">
          <div className="relative flex-grow">
            <input 
              type="text" 
              placeholder="Search schools..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-2 pl-8 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <SearchIcon 
              className="absolute left-2 top-3 text-gray-400" 
              size={18} 
            />
          </div>
        </div>

        {/* Performance Chart */}
        <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Network Performance Comparison
          </h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                interval={0}
                height={150}
              />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  Number(value).toFixed(2), 
                  name === 'mean' ? 'Mean Score' : 'Max Score'
                ]}
              />
              <Legend />
              <Bar 
                dataKey="mean" 
                fill="#8884d8" 
                name="Mean Performance" 
              />
              <Bar 
                dataKey="max" 
                fill="#82ca9d" 
                name="Max Performance" 
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Table */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Detailed Performance Metrics
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th 
                    className="p-3 text-left  cursor-pointer hover:bg-gray-200"
                    onClick={() => handleSort('name')}
                  >
                    School Name
                  </th>
                  <th 
                    className="p-3 text-right cursor-pointer hover:bg-gray-200"
                    onClick={() => handleSort('mean')}
                  >
                    <div className="flex items-center justify-end">
                      Mean Score 
                      {sortConfig.key === 'mean' && (
                        sortConfig.direction === 'ascending' 
                          ? <ChevronUpIcon size={18} /> 
                          : <ChevronDownIcon size={18} />
                      )}
                    </div>
                  </th>
                  <th 
                    className="p-3 text-right cursor-pointer hover:bg-gray-200"
                    onClick={() => handleSort('max')}
                  >
                    <div className="flex items-center justify-end">
                      Max Score
                      {sortConfig.key === 'max' && (
                        sortConfig.direction === 'ascending' 
                          ? <ChevronUpIcon size={18} /> 
                          : <ChevronDownIcon size={18} />
                      )}
                    </div>
                  </th>
                  <th 
                    className="p-3 text-right cursor-pointer hover:bg-gray-200"
                    onClick={() => handleSort('std')}
                  >
                    <div className="flex items-center justify-end">
                      Variability
                      {sortConfig.key === 'std' && (
                        sortConfig.direction === 'ascending' 
                          ? <ChevronUpIcon size={18} /> 
                          : <ChevronDownIcon size={18} />
                      )}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((school) => (
                  <tr key={school.name} className="border-b hover:bg-gray-50">
                    <td className="p-3 line-clamp-1 leading-8">{school.name}</td>
                    <td className="p-3 text-right">{school.mean.toFixed(2)}</td>
                    <td className="p-3 text-right">{school.max.toFixed(2)}</td>
                    <td className="p-3 text-right">{school.std.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchoolPerformanceDashboard;