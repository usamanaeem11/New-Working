import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';

const SkillMatrix = () => {
  const [skills, setSkills] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadSkills();
    loadEmployees();
  }, []);

  const loadSkills = async () => {
    try {
      const response = await axios.get('/api/resource-planning/skills');
      setSkills(response.data.skills || []);
    } catch (error) {
      message.error('Failed to load skills');
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await axios.get('/api/employees');
      setEmployees(response.data.employees || []);
    } catch (error) {
      console.error('Failed to load employees');
    }
  };

  const addEmployeeSkill = async (values) => {
    try {
      await axios.post(`/api/resource-planning/employees/${values.employee_id}/skills`, values);
      message.success('Skill added');
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to add skill');
    }
  };

  const columns = [
    { title: 'Skill', dataIndex: 'name', key: 'name' },
    { title: 'Category', dataIndex: 'category', key: 'category', render: (cat) => <Tag>{cat}</Tag> },
    { title: 'Employees', dataIndex: 'employee_count', key: 'employee_count' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1>Skill Matrix</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Add Skill to Employee
        </Button>
      </div>

      <Card>
        <Table dataSource={skills} columns={columns} rowKey="skill_id" />
      </Card>

      <Modal title="Add Skill" visible={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} onFinish={addEmployeeSkill} layout="vertical">
          <Form.Item name="employee_id" label="Employee" rules={[{ required: true }]}>
            <Select>{employees.map(e => <Select.Option key={e.id} value={e.id}>{e.name}</Select.Option>)}</Select>
          </Form.Item>
          <Form.Item name="skill_id" label="Skill" rules={[{ required: true }]}>
            <Select>{skills.map(s => <Select.Option key={s.skill_id} value={s.skill_id}>{s.name}</Select.Option>)}</Select>
          </Form.Item>
          <Form.Item name="proficiency_level" label="Proficiency (1-5)" rules={[{ required: true }]}>
            <Select>
              {[1,2,3,4,5].map(n => <Select.Option key={n} value={n}>{n}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="years_experience" label="Years Experience">
            <Input type="number" step="0.5" />
          </Form.Item>
          <Form.Item name="certified" valuePropName="checked">
            <input type="checkbox" /> Certified
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Add Skill</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default SkillMatrix;
