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
