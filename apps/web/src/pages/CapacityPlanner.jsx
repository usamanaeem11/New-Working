import React, { useState, useEffect } from 'react';
import { Card, Select, DatePicker, Button } from 'antd';
import axios from 'axios';

const { RangePicker } = DatePicker;

const CapacityPlanner = () => {
  const [capacityData, setCapacityData] = useState(null);
  const [dateRange, setDateRange] = useState([]);

  const loadCapacity = async () => {
    if (dateRange.length === 2) {
      try {
        const response = await axios.get('/api/resource-planning/capacity/organization', {
          params: {
            start_date: dateRange[0].format('YYYY-MM-DD'),
            end_date: dateRange[1].format('YYYY-MM-DD'),
          }
        });
        setCapacityData(response.data);
      } catch (error) {
        console.error('Failed to load capacity');
      }
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>Capacity Planner</h1>
      
      <Card style={{ marginBottom: '24px' }}>
        <RangePicker onChange={setDateRange} style={{ marginRight: '16px' }} />
        <Button type="primary" onClick={loadCapacity}>Load Capacity</Button>
      </Card>

      {capacityData && (
        <Card title="Organization Capacity">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            <div>
              <h3>Total Employees</h3>
              <h2>{capacityData.total_employees}</h2>
            </div>
            <div>
              <h3>Total Capacity</h3>
              <h2>{capacityData.total_capacity}h</h2>
            </div>
            <div>
              <h3>Total Allocated</h3>
              <h2>{capacityData.total_allocated}h</h2>
            </div>
            <div>
              <h3>Avg Utilization</h3>
              <h2>{capacityData.average_utilization}%</h2>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CapacityPlanner;
