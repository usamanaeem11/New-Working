import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tag, Modal, Form, Input, Select, Rate, Tabs, Progress, message } from 'antd';
import { PlusOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { TextArea } = Input;

const PerformanceReviews = () => {
  const [reviews, setReviews] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [reviewModal, setReviewModal] = useState(false);
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  const [form] = Form.useForm();
  const [feedbackForm] = Form.useForm();

  useEffect(() => {
    loadReviews();
    loadCycles();
  }, []);

  const loadReviews = async () => {
    try {
      const response = await axios.get('/api/performance/reviews');
      setReviews(response.data.reviews || []);
    } catch (error) {
      message.error('Failed to load reviews');
    }
  };

  const loadCycles = async () => {
    try {
      const response = await axios.get('/api/performance/cycles');
      setCycles(response.data.cycles || []);
    } catch (error) {
      message.error('Failed to load cycles');
    }
  };

  const createReview = async (values) => {
    try {
      await axios.post('/api/performance/reviews', {
        ...values,
        reviewer_id: localStorage.getItem('user_id'),
      });
      message.success('Review created');
      setReviewModal(false);
      form.resetFields();
      loadReviews();
    } catch (error) {
      message.error('Failed to create review');
    }
  };

  const submitFeedback = async (values) => {
    try {
      await axios.post(`/api/performance/reviews/${selectedReview.review_id}/feedback`, {
        ...values,
        reviewer_id: localStorage.getItem('user_id'),
      });
      message.success('Feedback submitted');
      setFeedbackModal(false);
      feedbackForm.resetFields();
    } catch (error) {
      message.error('Failed to submit feedback');
    }
  };

  const completeReview = async (reviewId) => {
    try {
      await axios.post(`/api/performance/reviews/${reviewId}/complete`);
      message.success('Review completed');
      loadReviews();
    } catch (error) {
      message.error('Failed to complete review');
    }
  };

  const reviewColumns = [
    {
      title: 'Employee',
      dataIndex: 'employee_name',
      key: 'employee_name',
    },
    {
      title: 'Reviewer',
      dataIndex: 'reviewer_name',
      key: 'reviewer_name',
    },
    {
      title: 'Cycle',
      dataIndex: 'cycle_name',
      key: 'cycle_name',
    },
    {
      title: 'Type',
      dataIndex: 'review_type',
      key: 'review_type',
      render: (type) => <Tag>{type}</Tag>,
    },
    {
      title: 'Rating',
      dataIndex: 'overall_rating',
      key: 'overall_rating',
      render: (rating) => rating ? <Rate disabled value={rating} /> : 'N/A',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'completed' ? 'green' : status === 'submitted' ? 'blue' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div>
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => {
              setSelectedReview(record);
              setFeedbackModal(true);
            }}
            style={{ marginRight: 8 }}
          >
            View
          </Button>
          {record.status === 'draft' && (
            <Button
              type="primary"
              size="small"
              onClick={() => completeReview(record.review_id)}
            >
              Complete
            </Button>
          )}
        </div>
      ),
    },
  ];

  const cycleColumns = [
    {
      title: 'Cycle Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'cycle_type',
      key: 'cycle_type',
      render: (type) => <Tag>{type}</Tag>,
    },
    {
      title: 'Period',
      key: 'period',
      render: (_, record) => `${record.start_date} to ${record.end_date}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : status === 'completed' ? 'blue' : 'default'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Progress',
      key: 'progress',
      render: (_, record) => (
        <Progress
          percent={(record.reviews_completed / record.reviews_count) * 100}
          format={() => `${record.reviews_completed}/${record.reviews_count}`}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Performance Reviews</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setReviewModal(true)}
        >
          Create Review
        </Button>
      </div>

      <Tabs defaultActiveKey="reviews">
        <TabPane tab="Reviews" key="reviews">
          <Card>
            <Table
              dataSource={reviews}
              columns={reviewColumns}
              rowKey="review_id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        <TabPane tab="Review Cycles" key="cycles">
          <Card>
            <Table
              dataSource={cycles}
              columns={cycleColumns}
              rowKey="cycle_id"
            />
          </Card>
        </TabPane>

        <TabPane tab="Analytics" key="analytics">
          <Card title="Review Analytics">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              <div>
                <h3>Average Rating</h3>
                <Rate disabled value={4.2} />
                <p>4.2 / 5.0</p>
              </div>
              <div>
                <h3>Completion Rate</h3>
                <Progress type="circle" percent={85} />
              </div>
              <div>
                <h3>Total Reviews</h3>
                <h2>{reviews.length}</h2>
              </div>
            </div>
          </Card>
        </TabPane>
      </Tabs>

      {/* Create Review Modal */}
      <Modal
        title="Create Performance Review"
        visible={reviewModal}
        onCancel={() => setReviewModal(false)}
        footer={null}
        width={700}
      >
        <Form form={form} onFinish={createReview} layout="vertical">
          <Form.Item name="cycle_id" label="Review Cycle" rules={[{ required: true }]}>
            <Select placeholder="Select cycle">
              {cycles.map(c => (
                <Select.Option key={c.cycle_id} value={c.cycle_id}>
                  {c.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="employee_id" label="Employee" rules={[{ required: true }]}>
            <Select placeholder="Select employee">
              <Select.Option value="emp_1">John Doe</Select.Option>
              <Select.Option value="emp_2">Jane Smith</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="review_type" label="Review Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="self">Self Assessment</Select.Option>
              <Select.Option value="manager">Manager Review</Select.Option>
              <Select.Option value="peer">Peer Review</Select.Option>
              <Select.Option value="360">360 Degree</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="overall_rating" label="Overall Rating">
            <Rate />
          </Form.Item>

          <Form.Item name="strengths" label="Strengths">
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item name="areas_for_improvement" label="Areas for Improvement">
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item name="goals_for_next_period" label="Goals for Next Period">
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create Review
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Feedback Modal */}
      <Modal
        title="Add 360 Feedback"
        visible={feedbackModal}
        onCancel={() => setFeedbackModal(false)}
        footer={null}
      >
        <Form form={feedbackForm} onFinish={submitFeedback} layout="vertical">
          <Form.Item name="feedback_type" label="Feedback Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="peer">Peer Feedback</Select.Option>
              <Select.Option value="manager">Manager Feedback</Select.Option>
              <Select.Option value="direct_report">Direct Report</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="rating" label="Rating">
            <Rate />
          </Form.Item>

          <Form.Item name="feedback_text" label="Feedback" rules={[{ required: true }]}>
            <TextArea rows={4} />
          </Form.Item>

          <Form.Item name="is_anonymous" valuePropName="checked">
            <input type="checkbox" /> Submit anonymously
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

export default PerformanceReviews;
