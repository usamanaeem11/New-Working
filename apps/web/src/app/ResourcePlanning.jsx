import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tag, Modal, Form, Input, Select, Progress, Tooltip } from 'antd';
import { UserOutlined, TeamOutlined, CalendarOutlined } from '@ant-design/icons';
import axios from 'axios';

const ResourcePlanning = () => {
  const [employees, setEmployees] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [capacityData, setCapacityData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [allocationModal, setAllocationModal] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadCapacityHeatmap();
    loadAllocations();
  }, []);

  const loadCapacityHeatmap = async () => {
    setLoading(true);
    try {
      const startDate = new Date().toISOString().split('T')[0];
      const endDate = new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0];
      
      const response = await axios.get('/api/resource-planning/capacity/heatmap', {
        params: { start_date: startDate, end_date: endDate, granularity: 'week' }
      });
      setCapacityData(response.data.heatmap_data || []);
    } catch (error) {
      console.error('Failed to load capacity data');
    }
    setLoading(false);
  };

  const loadAllocations = async () => {
    try {
      const response = await axios.get('/api/resource-planning/allocations');
      setAllocations(response.data.allocations || []);
    } catch (error) {
      console.error('Failed to load allocations');
    }
  };

  const createAllocation = async (values) => {
    try {
      await axios.post('/api/resource-planning/allocations', values);
      setAllocationModal(false);
      form.resetFields();
      loadAllocations();
      loadCapacityHeatmap();
    } catch (error) {
      console.error('Failed to create allocation');
    }
  };

  const getUtilizationColor = (utilization) => {
    if (utilization > 100) return '#ff4d4f'; // Overallocated - red
    if (utilization > 85) return '#faad14'; // High utilization - orange
    if (utilization > 70) return '#52c41a'; // Good utilization - green
    return '#1890ff'; // Low utilization - blue
  };

  const getUtilizationStatus = (utilization) => {
    if (utilization > 100) return 'overallocated';
    if (utilization > 85) return 'high';
    if (utilization > 70) return 'optimal';
    return 'low';
  };

  const capacityColumns = [
    {
      title: 'Employee',
      dataIndex: 'employee_name',
      key: 'employee_name',
      fixed: 'left',
      width: 150,
    },
    ...Array.from({ length: 4 }, (_, i) => ({
      title: `Week ${i + 1}`,
      key: `week_${i}`,
      width: 100,
      render: (_, record) => {
        const period = record.periods?.[i];
        if (!period) return '-';
        
        return (
          <Tooltip title={`${period.utilization}% utilized`}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={period.utilization}
                width={50}
                strokeColor={getUtilizationColor(period.utilization)}
                format={() => `${period.utilization}%`}
              />
            </div>
          </Tooltip>
        );
      },
    })),
    {
      title: 'Avg Utilization',
      key: 'avg',
      render: (_, record) => {
        const avg = record.periods?.reduce((sum, p) => sum + p.utilization, 0) / (record.periods?.length || 1);
        return (
          <Tag color={getUtilizationColor(avg)}>
            {avg.toFixed(1)}%
          </Tag>
        );
      },
    },
  ];

  const allocationColumns = [
    {
      title: 'Employee',
      dataIndex: 'employee_name',
      key: 'employee_name',
    },
    {
      title: 'Project',
      dataIndex: 'project_name',
      key: 'project_name',
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role) => <Tag>{role}</Tag>,
    },
    {
      title: 'Hours',
      dataIndex: 'hours_allocated',
      key: 'hours_allocated',
      render: (hours) => `${hours}h`,
    },
    {
      title: 'Period',
      key: 'period',
      render: (_, record) => `${record.start_date} to ${record.end_date}`,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Tag color={priority === 3 ? 'red' : priority === 2 ? 'orange' : 'default'}>
          {priority === 3 ? 'High' : priority === 2 ? 'Medium' : 'Low'}
        </Tag>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1>Resource Planning</h1>
        <Button type="primary" onClick={() => setAllocationModal(true)}>
          Create Allocation
        </Button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <UserOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
            <h3>{capacityData.length}</h3>
            <p>Total Resources</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <TeamOutlined style={{ fontSize: '32px', color: '#52c41a' }} />
            <h3>{allocations.length}</h3>
            <p>Active Allocations</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <CalendarOutlined style={{ fontSize: '32px', color: '#faad14' }} />
            <h3>78%</h3>
            <p>Avg Utilization</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center', color: '#ff4d4f' }}>
            <h3>5</h3>
            <p>Overallocated</p>
          </div>
        </Card>
      </div>

      {/* Capacity Heatmap */}
      <Card title="Capacity Heatmap (4 Week Forecast)" style={{ marginBottom: '24px' }}>
        <Table
          dataSource={capacityData}
          columns={capacityColumns}
          loading={loading}
          rowKey="employee_id"
          scroll={{ x: 800 }}
          pagination={false}
        />
      </Card>

      {/* Current Allocations */}
      <Card title="Current Resource Allocations">
        <Table
          dataSource={allocations}
          columns={allocationColumns}
          rowKey="allocation_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Allocation Modal */}
      <Modal
        title="Create Resource Allocation"
        visible={allocationModal}
        onCancel={() => setAllocationModal(false)}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={createAllocation} layout="vertical">
          <Form.Item name="employee_id" label="Employee" rules={[{ required: true }]}>
            <Select placeholder="Select employee">
              {/* Will be populated from API */}
              <Select.Option value="emp_1">John Doe</Select.Option>
              <Select.Option value="emp_2">Jane Smith</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="project_id" label="Project" rules={[{ required: true }]}>
            <Select placeholder="Select project">
              <Select.Option value="proj_1">Website Redesign</Select.Option>
              <Select.Option value="proj_2">Mobile App</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="role" label="Role" rules={[{ required: true }]}>
            <Input placeholder="e.g., Developer, Designer, QA" />
          </Form.Item>

          <Form.Item name="hours_allocated" label="Hours per Week" rules={[{ required: true }]}>
            <Input type="number" placeholder="40" />
          </Form.Item>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item name="start_date" label="Start Date" rules={[{ required: true }]}>
              <Input type="date" />
            </Form.Item>

            <Form.Item name="end_date" label="End Date" rules={[{ required: true }]}>
              <Input type="date" />
            </Form.Item>
          </div>

          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select>
              <Select.Option value={1}>Low</Select.Option>
              <Select.Option value={2}>Medium</Select.Option>
              <Select.Option value={3}>High</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create Allocation
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ResourcePlanning;
