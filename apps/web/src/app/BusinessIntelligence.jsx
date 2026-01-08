import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Select } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import axios from 'axios';

const BusinessIntelligence = () => {
  const [kpis, setKpis] = useState([]);
  const [profitability, setProfitability] = useState([]);

  useEffect(() => {
    loadKPIs();
    loadProfitability();
  }, []);

  const loadKPIs = async () => {
    try {
      const response = await axios.get('/api/bi/kpis');
      setKpis(response.data.kpis || []);
    } catch (error) {
      console.error('Failed to load KPIs');
    }
  };

  const loadProfitability = async () => {
    try {
      const response = await axios.get('/api/bi/profitability/projects');
      setProfitability(response.data.projects || []);
    } catch (error) {
      console.error('Failed to load profitability');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>Business Intelligence Dashboard</h1>
      
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {kpis.map((kpi) => (
          <Col span={6} key={kpi.kpi_id}>
            <Card>
              <Statistic
                title={kpi.name}
                value={kpi.current_value}
                precision={2}
                valueStyle={{ color: kpi.status === 'good' ? '#3f8600' : '#cf1322' }}
                prefix={kpi.status === 'good' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix={kpi.unit === 'percentage' ? '%' : ''}
              />
              <Progress
                percent={(kpi.current_value / kpi.target_value) * 100}
                status={kpi.status === 'good' ? 'success' : 'exception'}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="Project Profitability">
        <Table
          dataSource={profitability}
          columns={[
            { title: 'Project', dataIndex: 'project_name', key: 'project_name' },
            { title: 'Revenue', dataIndex: 'revenue', key: 'revenue', render: (v) => `$${v.toLocaleString()}` },
            { title: 'Cost', dataIndex: 'cost', key: 'cost', render: (v) => `$${v.toLocaleString()}` },
            { title: 'Profit', dataIndex: 'profit', key: 'profit', render: (v) => `$${v.toLocaleString()}` },
            { title: 'Margin', dataIndex: 'profit_margin', key: 'profit_margin', render: (v) => `${v}%` },
          ]}
          rowKey="project_id"
        />
      </Card>
    </div>
  );
};

export default BusinessIntelligence;
