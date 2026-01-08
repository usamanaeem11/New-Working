#!/bin/bash

# SkillMatrix.jsx
cat > SkillMatrix.jsx << 'EOF'
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
EOF

# PendingApprovals.jsx
cat > PendingApprovals.jsx << 'EOF'
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
EOF

# CustomDashboard.jsx
cat > CustomDashboard.jsx << 'EOF'
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
EOF

# WellnessGoals.jsx
cat > WellnessGoals.jsx << 'EOF'
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
EOF

# ReviewCycle.jsx
cat > ReviewCycle.jsx << 'EOF'
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
EOF

# ClientProjects.jsx
cat > ClientProjects.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Progress, Tabs } from 'antd';
import axios from 'axios';

const { TabPane } = Tabs;

const ClientProjects = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await axios.get('/api/client-portal/projects');
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Failed to load projects');
    }
  };

  const columns = [
    { title: 'Project', dataIndex: 'name', key: 'name' },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (s) => <Tag color={s === 'active' ? 'green' : 'blue'}>{s}</Tag> },
    { title: 'Progress', dataIndex: 'progress', key: 'progress', render: (p) => <Progress percent={p} /> },
    { title: 'Budget', dataIndex: 'budget', key: 'budget', render: (b) => `$${b.toLocaleString()}` },
    { title: 'Team', dataIndex: 'team_size', key: 'team_size' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>My Projects</h1>
      <Card>
        <Table
          dataSource={projects}
          columns={columns}
          rowKey="project_id"
          onRow={(record) => ({ onClick: () => setSelectedProject(record) })}
        />
      </Card>

      {selectedProject && (
        <Card title={selectedProject.name} style={{ marginTop: '24px' }}>
          <Tabs>
            <TabPane tab="Overview" key="overview">
              <p><strong>Status:</strong> {selectedProject.status}</p>
              <p><strong>Progress:</strong> {selectedProject.progress}%</p>
              <p><strong>Budget:</strong> ${selectedProject.budget.toLocaleString()}</p>
            </TabPane>
            <TabPane tab="Team" key="team">
              <p>Team size: {selectedProject.team_size}</p>
            </TabPane>
          </Tabs>
        </Card>
      )}
    </div>
  );
};

export default ClientProjects;
EOF

# ClientInvoices.jsx
cat > ClientInvoices.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const ClientInvoices = () => {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const response = await axios.get('/api/client-portal/invoices');
      setInvoices(response.data.invoices || []);
    } catch (error) {
      console.error('Failed to load invoices');
    }
  };

  const columns = [
    { title: 'Invoice #', dataIndex: 'invoice_number', key: 'invoice_number' },
    { title: 'Project', dataIndex: 'project_name', key: 'project_name' },
    { title: 'Amount', dataIndex: 'amount', key: 'amount', render: (a) => `$${a.toLocaleString()}` },
    { title: 'Date', dataIndex: 'invoice_date', key: 'invoice_date' },
    { title: 'Due Date', dataIndex: 'due_date', key: 'due_date' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status', 
      render: (s) => <Tag color={s === 'paid' ? 'green' : s === 'overdue' ? 'red' : 'orange'}>{s}</Tag> 
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button icon={<DownloadOutlined />} onClick={() => window.open(record.pdf_url, '_blank')}>
          Download
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Invoices</h1>
      <Card>
        <Table dataSource={invoices} columns={columns} rowKey="invoice_id" />
      </Card>
    </div>
  );
};

export default ClientInvoices;
EOF

# CapacityPlanner.jsx
cat > CapacityPlanner.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, Select, DatePicker, Button } from 'antd';
import axios from 'axios';

const { RangePicker } = DatePicker;

const CapacityPlanner = () => {
  const [capacityData, setCapacityData] = useState(null);
  const [dateRange, setDateRange] = useState([]);

  const loadCapacity = async () => {
    if (dateRange.length === 2) {
      try {
        const response = await axios.get('/api/resource-planning/capacity/organization', {
          params: {
            start_date: dateRange[0].format('YYYY-MM-DD'),
            end_date: dateRange[1].format('YYYY-MM-DD'),
          }
        });
        setCapacityData(response.data);
      } catch (error) {
        console.error('Failed to load capacity');
      }
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>Capacity Planner</h1>
      
      <Card style={{ marginBottom: '24px' }}>
        <RangePicker onChange={setDateRange} style={{ marginRight: '16px' }} />
        <Button type="primary" onClick={loadCapacity}>Load Capacity</Button>
      </Card>

      {capacityData && (
        <Card title="Organization Capacity">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            <div>
              <h3>Total Employees</h3>
              <h2>{capacityData.total_employees}</h2>
            </div>
            <div>
              <h3>Total Capacity</h3>
              <h2>{capacityData.total_capacity}h</h2>
            </div>
            <div>
              <h3>Total Allocated</h3>
              <h2>{capacityData.total_allocated}h</h2>
            </div>
            <div>
              <h3>Avg Utilization</h3>
              <h2>{capacityData.average_utilization}%</h2>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CapacityPlanner;
EOF

echo "✅ Created all 7 remaining pages (9-15/15)"
