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
