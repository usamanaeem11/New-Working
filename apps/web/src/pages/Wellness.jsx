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
