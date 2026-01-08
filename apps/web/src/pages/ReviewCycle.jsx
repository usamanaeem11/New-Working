import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Modal, Form, Input, Select, DatePicker, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const ReviewCycle = () => {
  const [cycles, setCycles] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadCycles();
  }, []);

  const loadCycles = async () => {
    try {
      const response = await axios.get('/api/performance/cycles');
      setCycles(response.data.cycles || []);
    } catch (error) {
      message.error('Failed to load cycles');
    }
  };

  const createCycle = async (values) => {
    try {
      await axios.post('/api/performance/cycles', {
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD'),
      });
      message.success('Cycle created');
      setModalVisible(false);
      form.resetFields();
      loadCycles();
    } catch (error) {
      message.error('Failed to create cycle');
    }
  };

  const columns = [
    { title: 'Cycle Name', dataIndex: 'name', key: 'name' },
    { title: 'Type', dataIndex: 'cycle_type', key: 'cycle_type' },
    { title: 'Start Date', dataIndex: 'start_date', key: 'start_date' },
    { title: 'End Date', dataIndex: 'end_date', key: 'end_date' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Review Cycles</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Create Cycle
        </Button>
      </div>

      <Card>
        <Table dataSource={cycles} columns={columns} rowKey="cycle_id" />
      </Card>

      <Modal title="Create Review Cycle" visible={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} onFinish={createCycle} layout="vertical">
          <Form.Item name="name" label="Cycle Name" rules={[{ required: true }]}>
            <Input placeholder="Q1 2024 Performance Review" />
          </Form.Item>
          <Form.Item name="cycle_type" label="Cycle Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="annual">Annual</Select.Option>
              <Select.Option value="quarterly">Quarterly</Select.Option>
              <Select.Option value="probation">Probation</Select.Option>
              <Select.Option value="mid_year">Mid-Year</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="start_date" label="Start Date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="end_date" label="End Date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Create Cycle</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default ReviewCycle;
