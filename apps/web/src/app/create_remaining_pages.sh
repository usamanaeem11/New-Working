#!/bin/bash

# Create WorkflowBuilder.jsx
cat > WorkflowBuilder.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Button, Steps, Form, Input, Select, Table, Modal, message } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

const WorkflowBuilder = () => {
  const [workflows, setWorkflows] = useState([]);
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [steps, setSteps] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      const response = await axios.get('/api/workflows/definitions');
      setWorkflows(response.data.workflows || []);
    } catch (error) {
      message.error('Failed to load workflows');
    }
  };

  const createWorkflow = async (values) => {
    try {
      await axios.post('/api/workflows/definitions', values);
      message.success('Workflow created');
      setModalVisible(false);
      loadWorkflows();
    } catch (error) {
      message.error('Failed to create workflow');
    }
  };

  const addApprovalStep = async (workflowId, stepData) => {
    try {
      await axios.post(`/api/workflows/definitions/${workflowId}/steps`, stepData);
      message.success('Step added');
    } catch (error) {
      message.error('Failed to add step');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Workflow Builder</h1>
        <Button type="primary" onClick={() => setModalVisible(true)}>
          Create Workflow
        </Button>
      </div>

      <Card title="Available Workflows">
        <Table
          dataSource={workflows}
          columns={[
            { title: 'Name', dataIndex: 'name', key: 'name' },
            { title: 'Trigger', dataIndex: 'trigger_type', key: 'trigger_type' },
            { title: 'Steps', dataIndex: 'steps_count', key: 'steps_count' },
            { title: 'Active', dataIndex: 'is_active', key: 'is_active', render: (v) => v ? 'Yes' : 'No' },
          ]}
          rowKey="workflow_id"
        />
      </Card>

      <Modal
        title="Create Workflow"
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={createWorkflow} layout="vertical">
          <Form.Item name="name" label="Workflow Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="trigger_type" label="Trigger Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="expense">Expense</Select.Option>
              <Select.Option value="leave">Leave Request</Select.Option>
              <Select.Option value="timesheet">Timesheet</Select.Option>
              <Select.Option value="invoice">Invoice</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>Create</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowBuilder;
EOF

# Create BusinessIntelligence.jsx
cat > BusinessIntelligence.jsx << 'EOF'
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
EOF

# Create Wellness.jsx
cat > Wellness.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Button, Form, Slider, Input, Rate, Progress, Table, message } from 'antd';
import { SmileOutlined, FrownOutlined } from '@ant-design/icons';
import axios from 'axios';

const Wellness = () => {
  const [checkins, setCheckins] = useState([]);
  const [goals, setGoals] = useState([]);
  const [trends, setTrends] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadCheckins();
    loadGoals();
    loadTrends();
  }, []);

  const loadCheckins = async () => {
    try {
      const employeeId = localStorage.getItem('employee_id');
      const response = await axios.get(`/api/wellness/checkins?employee_id=${employeeId}`);
      setCheckins(response.data.checkins || []);
    } catch (error) {
      console.error('Failed to load check-ins');
    }
  };

  const loadGoals = async () => {
    try {
      const employeeId = localStorage.getItem('employee_id');
      const response = await axios.get(`/api/wellness/goals?employee_id=${employeeId}`);
      setGoals(response.data.goals || []);
    } catch (error) {
      console.error('Failed to load goals');
    }
  };

  const loadTrends = async () => {
    try {
      const employeeId = localStorage.getItem('employee_id');
      const response = await axios.get(`/api/wellness/checkins/trends?employee_id=${employeeId}&period=30days`);
      setTrends(response.data);
    } catch (error) {
      console.error('Failed to load trends');
    }
  };

  const submitCheckin = async (values) => {
    try {
      const employeeId = localStorage.getItem('employee_id');
      await axios.post('/api/wellness/checkins', { ...values, employee_id: employeeId });
      message.success('Check-in submitted');
      form.resetFields();
      loadCheckins();
      loadTrends();
    } catch (error) {
      message.error('Failed to submit check-in');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>Employee Wellness</h1>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="Daily Check-in">
            <Form form={form} onFinish={submitCheckin} layout="vertical">
              <Form.Item name="mood" label="Mood (1-5)" rules={[{ required: true }]}>
                <Slider min={1} max={5} marks={{ 1: '😢', 3: '😐', 5: '😊' }} />
              </Form.Item>
              <Form.Item name="stress_level" label="Stress Level (1-5)" rules={[{ required: true }]}>
                <Slider min={1} max={5} marks={{ 1: 'Low', 3: 'Medium', 5: 'High' }} />
              </Form.Item>
              <Form.Item name="energy_level" label="Energy Level (1-5)" rules={[{ required: true }]}>
                <Slider min={1} max={5} marks={{ 1: 'Low', 3: 'Medium', 5: 'High' }} />
              </Form.Item>
              <Form.Item name="sleep_hours" label="Hours of Sleep">
                <Input type="number" step="0.5" placeholder="7.5" />
              </Form.Item>
              <Form.Item name="notes" label="Notes">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Button type="primary" htmlType="submit" block>Submit Check-in</Button>
            </Form>
          </Card>
        </Col>

        <Col span={12}>
          <Card title="Wellness Trends">
            {trends && (
              <>
                <div style={{ marginBottom: '16px' }}>
                  <h4>Average Scores (Last 30 Days)</h4>
                  <p>Mood: {trends.averages?.mood}/5</p>
                  <p>Stress: {trends.averages?.stress_level}/5</p>
                  <p>Energy: {trends.averages?.energy_level}/5</p>
                  <p>Sleep: {trends.averages?.sleep_hours}h</p>
                </div>
                <h4>Insights</h4>
                {trends.insights?.map((insight, i) => (
                  <p key={i}>{insight}</p>
                ))}
              </>
            )}
          </Card>

          <Card title="Wellness Goals" style={{ marginTop: '16px' }}>
            {goals.map((goal) => (
              <div key={goal.goal_id} style={{ marginBottom: '16px' }}>
                <p>{goal.goal_type}: {goal.target_value}</p>
                <Progress percent={goal.progress_percentage} />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Wellness;
EOF

# Create OKRs.jsx
cat > OKRs.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Button, Form, Input, Progress, Tree, Modal, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';

const OKRs = () => {
  const [okrs, setOkrs] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadOKRs();
  }, []);

  const loadOKRs = async () => {
    try {
      const response = await axios.get('/api/performance/okrs');
      setOkrs(response.data.okrs || []);
    } catch (error) {
      message.error('Failed to load OKRs');
    }
  };

  const createOKR = async (values) => {
    try {
      await axios.post('/api/performance/okrs', {
        ...values,
        owner_id: localStorage.getItem('user_id'),
        quarter: getCurrentQuarter(),
        year: new Date().getFullYear(),
      });
      message.success('OKR created');
      setModalVisible(false);
      loadOKRs();
    } catch (error) {
      message.error('Failed to create OKR');
    }
  };

  const getCurrentQuarter = () => {
    const month = new Date().getMonth() + 1;
    return `${new Date().getFullYear()}-Q${Math.ceil(month / 3)}`;
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>OKRs & Goals</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Create OKR
        </Button>
      </div>

      {okrs.map((okr) => (
        <Card key={okr.okr_id} style={{ marginBottom: '16px' }}>
          <h3>{okr.objective}</h3>
          <p>Owner: {okr.owner_name} | Quarter: {okr.quarter}</p>
          <Progress percent={okr.progress_percentage} status={okr.status === 'on_track' ? 'success' : 'exception'} />
          
          <div style={{ marginTop: '16px' }}>
            <h4>Key Results:</h4>
            {okr.key_results?.map((kr, i) => (
              <div key={i} style={{ marginBottom: '8px' }}>
                <p>{kr.description}</p>
                <Progress percent={(kr.current / kr.target) * 100} format={() => `${kr.current}/${kr.target}`} />
              </div>
            ))}
          </div>
        </Card>
      ))}

      <Modal
        title="Create OKR"
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={createOKR} layout="vertical">
          <Form.Item name="objective" label="Objective" rules={[{ required: true }]}>
            <Input.TextArea rows={2} placeholder="What do you want to achieve?" />
          </Form.Item>
          <Form.Item label="Key Results (Add 2-5)">
            <Form.List name="key_results">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(field => (
                    <div key={field.key} style={{ marginBottom: '8px' }}>
                      <Input placeholder="Key result description" />
                    </div>
                  ))}
                  <Button onClick={() => add()}>Add Key Result</Button>
                </>
              )}
            </Form.List>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Create OKR</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default OKRs;
EOF

echo "✅ Created 5 more pages (3-7/15)"
