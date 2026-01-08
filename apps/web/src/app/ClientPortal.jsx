import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tag, Tabs, Rate, Modal, Form, Input, Upload, message } from 'antd';
import { ProjectOutlined, FileTextOutlined, DollarOutlined, StarOutlined, UploadOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { TextArea } = Input;

const ClientPortal = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [projects, setProjects] = useState([]);
  const [timesheets, setTimesheets] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadDashboard();
    loadProjects();
    loadTimesheets();
    loadInvoices();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/client-portal/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      message.error('Failed to load dashboard');
    }
    setLoading(false);
  };

  const loadProjects = async () => {
    try {
      const response = await axios.get('/api/client-portal/projects');
      setProjects(response.data.projects || []);
    } catch (error) {
      message.error('Failed to load projects');
    }
  };

  const loadTimesheets = async () => {
    try {
      const response = await axios.get('/api/client-portal/timesheets/pending');
      setTimesheets(response.data.timesheets || []);
    } catch (error) {
      message.error('Failed to load timesheets');
    }
  };

  const loadInvoices = async () => {
    try {
      const response = await axios.get('/api/client-portal/invoices');
      setInvoices(response.data.invoices || []);
    } catch (error) {
      message.error('Failed to load invoices');
    }
  };

  const approveTimesheet = async (timesheetId) => {
    try {
      await axios.post(`/api/client-portal/timesheets/${timesheetId}/approve`);
      message.success('Timesheet approved successfully');
      loadTimesheets();
    } catch (error) {
      message.error('Failed to approve timesheet');
    }
  };

  const rejectTimesheet = async (timesheetId, reason) => {
    try {
      await axios.post(`/api/client-portal/timesheets/${timesheetId}/reject`, { reason });
      message.success('Timesheet rejected');
      loadTimesheets();
    } catch (error) {
      message.error('Failed to reject timesheet');
    }
  };

  const submitFeedback = async (values) => {
    try {
      await axios.post('/api/client-portal/feedback', values);
      message.success('Feedback submitted successfully');
      setFeedbackModal(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to submit feedback');
    }
  };

  const projectColumns = [
    {
      title: 'Project Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : status === 'completed' ? 'blue' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress) => `${progress}%`,
    },
    {
      title: 'Budget',
      dataIndex: 'budget',
      key: 'budget',
      render: (budget) => `$${budget.toLocaleString()}`,
    },
    {
      title: 'Team Size',
      dataIndex: 'team_size',
      key: 'team_size',
    },
  ];

  const timesheetColumns = [
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
      title: 'Hours',
      dataIndex: 'total_hours',
      key: 'total_hours',
      render: (hours) => `${hours}h`,
    },
    {
      title: 'Period',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color="orange">{status}</Tag>,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div>
          <Button 
            type="primary" 
            size="small" 
            onClick={() => approveTimesheet(record.timesheet_id)}
            style={{ marginRight: 8 }}
          >
            Approve
          </Button>
          <Button 
            danger 
            size="small"
            onClick={() => {
              Modal.confirm({
                title: 'Reject Timesheet',
                content: (
                  <Input.TextArea 
                    placeholder="Reason for rejection"
                    id="reject-reason"
                  />
                ),
                onOk: () => {
                  const reason = document.getElementById('reject-reason').value;
                  rejectTimesheet(record.timesheet_id, reason);
                }
              });
            }}
          >
            Reject
          </Button>
        </div>
      ),
    },
  ];

  const invoiceColumns = [
    {
      title: 'Invoice #',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
    },
    {
      title: 'Project',
      dataIndex: 'project_name',
      key: 'project_name',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `$${amount.toLocaleString()}`,
    },
    {
      title: 'Date',
      dataIndex: 'invoice_date',
      key: 'invoice_date',
    },
    {
      title: 'Due Date',
      dataIndex: 'due_date',
      key: 'due_date',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'paid' ? 'green' : status === 'overdue' ? 'red' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button type="link" onClick={() => window.open(record.pdf_url, '_blank')}>
          Download PDF
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Client Portal</h1>
      
      {/* Dashboard Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <ProjectOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
            <h3>{dashboardData?.active_projects || 0}</h3>
            <p>Active Projects</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <FileTextOutlined style={{ fontSize: '32px', color: '#52c41a' }} />
            <h3>{dashboardData?.pending_timesheets || 0}</h3>
            <p>Pending Approvals</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <DollarOutlined style={{ fontSize: '32px', color: '#faad14' }} />
            <h3>${dashboardData?.total_invoiced?.toLocaleString() || 0}</h3>
            <p>Total Invoiced</p>
          </div>
        </Card>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <StarOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />
            <h3>{dashboardData?.satisfaction_score || 'N/A'}</h3>
            <p>Satisfaction Score</p>
          </div>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Card>
        <Tabs defaultActiveKey="projects">
          <TabPane tab="Projects" key="projects">
            <Table 
              dataSource={projects}
              columns={projectColumns}
              loading={loading}
              rowKey="project_id"
            />
          </TabPane>

          <TabPane tab={`Timesheets (${timesheets.length})`} key="timesheets">
            <Table 
              dataSource={timesheets}
              columns={timesheetColumns}
              loading={loading}
              rowKey="timesheet_id"
            />
          </TabPane>

          <TabPane tab="Invoices" key="invoices">
            <Table 
              dataSource={invoices}
              columns={invoiceColumns}
              loading={loading}
              rowKey="invoice_id"
            />
          </TabPane>

          <TabPane tab="Files" key="files">
            <Upload
              action="/api/client-portal/files/upload"
              listType="picture-card"
            >
              <div>
                <UploadOutlined />
                <div style={{ marginTop: 8 }}>Upload</div>
              </div>
            </Upload>
          </TabPane>
        </Tabs>
      </Card>

      {/* Feedback Button */}
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Button 
          type="primary" 
          icon={<StarOutlined />}
          onClick={() => setFeedbackModal(true)}
          size="large"
        >
          Provide Feedback
        </Button>
      </div>

      {/* Feedback Modal */}
      <Modal
        title="Submit Feedback"
        visible={feedbackModal}
        onCancel={() => setFeedbackModal(false)}
        footer={null}
      >
        <Form form={form} onFinish={submitFeedback} layout="vertical">
          <Form.Item
            name="project_id"
            label="Project"
            rules={[{ required: true, message: 'Please select a project' }]}
          >
            <select className="ant-input">
              <option value="">Select Project</option>
              {projects.map(p => (
                <option key={p.project_id} value={p.project_id}>{p.name}</option>
              ))}
            </select>
          </Form.Item>

          <Form.Item
            name="rating"
            label="Rating"
            rules={[{ required: true, message: 'Please provide a rating' }]}
          >
            <Rate />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true }]}
          >
            <select className="ant-input">
              <option value="service">Service Quality</option>
              <option value="communication">Communication</option>
              <option value="timeliness">Timeliness</option>
              <option value="quality">Work Quality</option>
            </select>
          </Form.Item>

          <Form.Item
            name="comments"
            label="Comments"
            rules={[{ required: true, message: 'Please provide comments' }]}
          >
            <TextArea rows={4} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Submit Feedback
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ClientPortal;
