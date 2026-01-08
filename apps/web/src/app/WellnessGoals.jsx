import React, { useState, useEffect } from 'react';
import { Card, Progress, Button, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined, TrophyOutlined } from '@ant-design/icons';
import axios from 'axios';

const WellnessGoals = () => {
  const [goals, setGoals] = useState([]);
  const [challenges, setChallenges] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadGoals();
    loadChallenges();
  }, []);

  const loadGoals = async () => {
    try {
      const empId = localStorage.getItem('employee_id');
      const response = await axios.get(`/api/wellness/goals?employee_id=${empId}`);
      setGoals(response.data.goals || []);
    } catch (error) {
      console.error('Failed to load goals');
    }
  };

  const loadChallenges = async () => {
    try {
      const response = await axios.get('/api/wellness/challenges');
      setChallenges(response.data.active_challenges || []);
    } catch (error) {
      console.error('Failed to load challenges');
    }
  };

  const createGoal = async (values) => {
    try {
      await axios.post('/api/wellness/goals', {
        ...values,
        employee_id: localStorage.getItem('employee_id'),
      });
      message.success('Goal created');
      setModalVisible(false);
      form.resetFields();
      loadGoals();
    } catch (error) {
      message.error('Failed to create goal');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Wellness Goals</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Create Goal
        </Button>
      </div>

      <h2>My Goals</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {goals.map(goal => (
          <Card key={goal.goal_id}>
            <h3>{goal.goal_type}</h3>
            <p>Target: {goal.target_value} {goal.frequency}</p>
            <Progress percent={goal.progress_percentage} />
            <p>Streak: {goal.streak_days} days 🔥</p>
          </Card>
        ))}
      </div>

      <h2>Team Challenges</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
        {challenges.map(challenge => (
          <Card key={challenge.challenge_id}>
            <h3><TrophyOutlined /> {challenge.name}</h3>
            <p>Goal: {challenge.goal_value} {challenge.challenge_type}</p>
            <p>Participants: {challenge.participants}</p>
            <p>Duration: {challenge.duration_days} days</p>
          </Card>
        ))}
      </div>

      <Modal title="Create Wellness Goal" visible={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} onFinish={createGoal} layout="vertical">
          <Form.Item name="goal_type" label="Goal Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="exercise">Exercise</Select.Option>
              <Select.Option value="meditation">Meditation</Select.Option>
              <Select.Option value="breaks">Regular Breaks</Select.Option>
              <Select.Option value="sleep">Sleep</Select.Option>
              <Select.Option value="hydration">Hydration</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="target_value" label="Target" rules={[{ required: true }]}>
            <Input type="number" placeholder="e.g., 30 minutes" />
          </Form.Item>
          <Form.Item name="frequency" label="Frequency" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="daily">Daily</Select.Option>
              <Select.Option value="weekly">Weekly</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="start_date" label="Start Date" rules={[{ required: true }]}>
            <Input type="date" />
          </Form.Item>
          <Form.Item name="end_date" label="End Date" rules={[{ required: true }]}>
            <Input type="date" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Create Goal</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default WellnessGoals;
