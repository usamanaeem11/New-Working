import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Tabs, Input, List, Avatar, Badge, Modal, Form, Select, Upload, message } from 'antd';
import { 
  VideoCameraOutlined, 
  PhoneOutlined, 
  MailOutlined, 
  WhatsAppOutlined,
  CalendarOutlined,
  DesktopOutlined,
  FileOutlined,
  RecordOutlined,
  UserAddOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { TextArea } = Input;

const Communications = () => {
  const [activeTab, setActiveTab] = useState('email');
  const [emails, setEmails] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [activeCall, setActiveCall] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [emailModal, setEmailModal] = useState(false);
  const [meetingModal, setMeetingModal] = useState(false);
  const [form] = Form.useForm();
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnection = useRef(null);

  useEffect(() => {
    loadEmails();
    loadMeetings();
  }, []);

  const loadEmails = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const response = await axios.get(`/api/communications/email/inbox?user_id=${userId}`);
      setEmails(response.data.emails || []);
    } catch (error) {
      console.error('Failed to load emails');
    }
  };

  const loadMeetings = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const response = await axios.get(`/api/communications/meetings?user_id=${userId}`);
      setMeetings(response.data.meetings || []);
    } catch (error) {
      console.error('Failed to load meetings');
    }
  };

  const sendEmail = async (values) => {
    try {
      await axios.post('/api/communications/email/send', {
        ...values,
        from_user_id: localStorage.getItem('user_id')
      });
      message.success('Email sent');
      setEmailModal(false);
      form.resetFields();
      loadEmails();
    } catch (error) {
      message.error('Failed to send email');
    }
  };

  const startVideoCall = async (userId) => {
    try {
      // Request media permissions
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // Create call session
      const response = await axios.post('/api/communications/calls/start', {
        call_type: 'video',
        initiator_id: localStorage.getItem('user_id'),
        participants: [userId]
      });

      setActiveCall(response.data);
      
      // Initialize WebRTC connection
      initializeWebRTC(response.data.session_id, stream);
      
      message.success('Call started');
    } catch (error) {
      message.error('Failed to start call');
    }
  };

  const initializeWebRTC = (sessionId, stream) => {
    // Create peer connection
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    // Add local stream
    stream.getTracks().forEach(track => pc.addTrack(track, stream));

    // Handle remote stream
    pc.ontrack = (event) => {
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = event.streams[0];
      }
    };

    // Connect to WebSocket for signaling
    const ws = new WebSocket(`ws://localhost:8000/api/communications/ws/${sessionId}`);
    
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        ws.send(JSON.stringify({ type: 'answer', answer }));
      } else if (data.type === 'answer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
      } else if (data.type === 'ice-candidate') {
        await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
      }
    };

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        ws.send(JSON.stringify({ type: 'ice-candidate', candidate: event.candidate }));
      }
    };

    peerConnection.current = pc;
  };

  const endCall = async () => {
    if (activeCall) {
      await axios.post(`/api/communications/calls/${activeCall.session_id}/end`);
      
      // Stop all tracks
      if (localVideoRef.current && localVideoRef.current.srcObject) {
        localVideoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      
      if (peerConnection.current) {
        peerConnection.current.close();
      }
      
      setActiveCall(null);
      message.success('Call ended');
    }
  };

  const startRecording = async () => {
    try {
      await axios.post(`/api/communications/calls/${activeCall.session_id}/record/start`);
      setIsRecording(true);
      message.success('Recording started');
    } catch (error) {
      message.error('Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      const response = await axios.post(`/api/communications/calls/${activeCall.session_id}/record/stop`);
      setIsRecording(false);
      message.success(`Recording saved: ${response.data.recording_url}`);
    } catch (error) {
      message.error('Failed to stop recording');
    }
  };

  const shareScreen = async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      
      // Replace video track with screen track
      const screenTrack = screenStream.getVideoTracks()[0];
      const sender = peerConnection.current.getSenders().find(s => s.track.kind === 'video');
      sender.replaceTrack(screenTrack);
      
      await axios.post('/api/communications/screen-share/start', {
        session_id: activeCall.session_id,
        user_id: localStorage.getItem('user_id')
      });
      
      message.success('Screen sharing started');
    } catch (error) {
      message.error('Failed to share screen');
    }
  };

  const sendWhatsApp = async (phoneNumber, message) => {
    try {
      await axios.post('/api/communications/whatsapp/send', {
        from_user_id: localStorage.getItem('user_id'),
        to_phone: phoneNumber,
        message
      });
      message.success('WhatsApp message sent');
    } catch (error) {
      message.error('Failed to send WhatsApp');
    }
  };

  const createMeeting = async (values) => {
    try {
      await axios.post('/api/communications/meetings', {
        ...values,
        organizer_id: localStorage.getItem('user_id')
      });
      message.success('Meeting scheduled');
      setMeetingModal(false);
      loadMeetings();
    } catch (error) {
      message.error('Failed to create meeting');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1>Communications Center</h1>

      {activeCall && (
        <Card style={{ marginBottom: '24px', background: '#f0f2f5' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <p>You</p>
              <video ref={localVideoRef} autoPlay muted style={{ width: '100%', borderRadius: '8px' }} />
            </div>
            <div>
              <p>Participant</p>
              <video ref={remoteVideoRef} autoPlay style={{ width: '100%', borderRadius: '8px' }} />
            </div>
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <Button icon={<DesktopOutlined />} onClick={shareScreen} style={{ marginRight: '8px' }}>
              Share Screen
            </Button>
            <Button 
              icon={<RecordOutlined />} 
              onClick={isRecording ? stopRecording : startRecording}
              type={isRecording ? 'primary' : 'default'}
              danger={isRecording}
              style={{ marginRight: '8px' }}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </Button>
            <Button danger onClick={endCall}>
              End Call
            </Button>
          </div>
        </Card>
      )}

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={<span><MailOutlined /> Email</span>} key="email">
          <Card
            extra={<Button type="primary" onClick={() => setEmailModal(true)}>Compose</Button>}
          >
            <List
              dataSource={emails}
              renderItem={(email) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar>{email.from_user[0]}</Avatar>}
                    title={email.subject}
                    description={`From: ${email.from_user} - ${email.preview}`}
                  />
                  <div>{email.sent_at}</div>
                </List.Item>
              )}
            />
          </Card>
        </TabPane>

        <TabPane tab={<span><VideoCameraOutlined /> Video Calls</span>} key="video">
          <Card>
            <Button 
              type="primary" 
              icon={<VideoCameraOutlined />}
              onClick={() => startVideoCall('user_2')}
              disabled={!!activeCall}
            >
              Start Video Call
            </Button>
            <p style={{ marginTop: '16px' }}>Select a user to call...</p>
          </Card>
        </TabPane>

        <TabPane tab={<span><WhatsAppOutlined /> WhatsApp</span>} key="whatsapp">
          <Card>
            <Form layout="vertical" onFinish={(values) => sendWhatsApp(values.phone, values.message)}>
              <Form.Item name="phone" label="Phone Number" rules={[{ required: true }]}>
                <Input placeholder="+1234567890" />
              </Form.Item>
              <Form.Item name="message" label="Message" rules={[{ required: true }]}>
                <TextArea rows={4} />
              </Form.Item>
              <Button type="primary" htmlType="submit">Send WhatsApp</Button>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab={<span><CalendarOutlined /> Meetings</span>} key="meetings">
          <Card
            extra={<Button type="primary" onClick={() => setMeetingModal(true)}>Schedule Meeting</Button>}
          >
            <List
              dataSource={meetings}
              renderItem={(meeting) => (
                <List.Item
                  actions={[
                    <Button type="link">Join</Button>,
                    <Button type="link">Details</Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<CalendarOutlined style={{ fontSize: '24px' }} />}
                    title={meeting.title}
                    description={`${meeting.start_time} - ${meeting.participants_count} participants`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* Email Compose Modal */}
      <Modal
        title="Compose Email"
        visible={emailModal}
        onCancel={() => setEmailModal(false)}
        footer={null}
        width={700}
      >
        <Form form={form} onFinish={sendEmail} layout="vertical">
          <Form.Item name="to_users" label="To" rules={[{ required: true }]}>
            <Select mode="tags" placeholder="Enter email addresses or select users" />
          </Form.Item>
          <Form.Item name="subject" label="Subject" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="body" label="Message" rules={[{ required: true }]}>
            <TextArea rows={6} />
          </Form.Item>
          <Form.Item name="attachments" label="Attachments">
            <Upload><Button icon={<FileOutlined />}>Attach Files</Button></Upload>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Send Email</Button>
        </Form>
      </Modal>

      {/* Schedule Meeting Modal */}
      <Modal
        title="Schedule Meeting"
        visible={meetingModal}
        onCancel={() => setMeetingModal(false)}
        footer={null}
      >
        <Form onFinish={createMeeting} layout="vertical">
          <Form.Item name="title" label="Meeting Title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="participants" label="Participants" rules={[{ required: true }]}>
            <Select mode="multiple" placeholder="Select participants" />
          </Form.Item>
          <Form.Item name="start_time" label="Start Time" rules={[{ required: true }]}>
            <Input type="datetime-local" />
          </Form.Item>
          <Form.Item name="meeting_type" label="Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="video">Video Conference</Select.Option>
              <Select.Option value="audio">Audio Call</Select.Option>
            </Select>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Schedule Meeting</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default Communications;
