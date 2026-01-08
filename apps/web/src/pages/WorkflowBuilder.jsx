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
