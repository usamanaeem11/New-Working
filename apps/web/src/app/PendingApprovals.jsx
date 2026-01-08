import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Input, message } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import axios from 'axios';

const PendingApprovals = () => {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/workflows/instances?status=pending');
      setApprovals(response.data.instances || []);
    } catch (error) {
      message.error('Failed to load approvals');
    }
    setLoading(false);
  };

  const approve = async (instanceId) => {
    try {
      await axios.post(`/api/workflows/instances/${instanceId}/approve`, {
        comments: 'Approved',
      });
      message.success('Approved');
      loadApprovals();
    } catch (error) {
      message.error('Failed to approve');
    }
  };

  const reject = async (instanceId) => {
    Modal.confirm({
      title: 'Reject Approval',
      content: <Input.TextArea placeholder="Reason for rejection" id="reject-reason" />,
      onOk: async () => {
        const reason = document.getElementById('reject-reason').value;
        try {
          await axios.post(`/api/workflows/instances/${instanceId}/reject`, { comments: reason });
          message.success('Rejected');
          loadApprovals();
        } catch (error) {
          message.error('Failed to reject');
        }
      }
    });
  };

  const columns = [
    { title: 'Type', dataIndex: 'workflow_name', key: 'workflow_name' },
    { title: 'Entity', dataIndex: 'entity_type', key: 'entity_type', render: (t) => <Tag>{t}</Tag> },
    { title: 'Initiated By', dataIndex: 'initiated_by', key: 'initiated_by' },
    { title: 'Step', dataIndex: 'current_step', key: 'current_step' },
    { title: 'Initiated', dataIndex: 'initiated_at', key: 'initiated_at' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div>
          <Button type="primary" icon={<CheckOutlined />} onClick={() => approve(record.instance_id)} style={{ marginRight: 8 }}>
            Approve
          </Button>
          <Button danger icon={<CloseOutlined />} onClick={() => reject(record.instance_id)}>
            Reject
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Pending Approvals</h1>
      <Card>
        <Table dataSource={approvals} columns={columns} loading={loading} rowKey="instance_id" />
      </Card>
    </div>
  );
};

export default PendingApprovals;
