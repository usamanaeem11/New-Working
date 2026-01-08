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
