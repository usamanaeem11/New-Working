import React, { useState } from 'react';
import { Card, Button, Row, Col, Modal, Form, Input, Select } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const CustomDashboard = () => {
  const [widgets, setWidgets] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const addWidget = (values) => {
    setWidgets([...widgets, { ...values, id: Date.now() }]);
    setModalVisible(false);
    form.resetFields();
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Custom Dashboard</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Add Widget
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {widgets.map(widget => (
          <Col span={widget.size || 8} key={widget.id}>
            <Card title={widget.title}>
              <p>Widget Type: {widget.type}</p>
              <p>Data Source: {widget.dataSource}</p>
            </Card>
          </Col>
        ))}
      </Row>

      <Modal title="Add Widget" visible={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} onFinish={addWidget} layout="vertical">
          <Form.Item name="title" label="Widget Title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="type" label="Widget Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="kpi_card">KPI Card</Select.Option>
              <Select.Option value="line_chart">Line Chart</Select.Option>
              <Select.Option value="bar_chart">Bar Chart</Select.Option>
              <Select.Option value="table">Table</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="dataSource" label="Data Source" rules={[{ required: true }]}>
            <Input placeholder="e.g., revenue_by_month" />
          </Form.Item>
          <Form.Item name="size" label="Widget Size">
            <Select defaultValue={8}>
              <Select.Option value={6}>Small</Select.Option>
              <Select.Option value={8}>Medium</Select.Option>
              <Select.Option value={12}>Large</Select.Option>
            </Select>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Add Widget</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default CustomDashboard;
