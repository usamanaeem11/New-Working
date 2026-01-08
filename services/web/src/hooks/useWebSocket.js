/**
 * WebSocket Hook for Real-time Updates
 * Connects to backend WebSocket and handles all real-time events
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (token) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [notifications, setNotifications] = useState([]);
  
  const connect = useCallback(() => {
    if (!token) return;
    
    // Connect to WebSocket
    const wsUrl = `ws://localhost:8000/api/ws?token=${token}`;
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message);
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Reconnect after 3 seconds
      setTimeout(connect, 3000);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [token]);
  
  const handleMessage = (message) => {
    console.log('WebSocket message:', message);
    
    switch (message.type) {
      case 'connection':
        console.log('Connection established:', message);
        break;
        
      case 'presence':
        setOnlineUsers(message.online_users || []);
        break;
        
      case 'user_presence':
        if (message.action === 'joined') {
          setOnlineUsers(prev => [...prev, message.user_id]);
        } else if (message.action === 'left') {
          setOnlineUsers(prev => prev.filter(id => id !== message.user_id));
        }
        break;
        
      case 'time_entry':
        // Real-time time entry notification
        addNotification({
          type: 'time_entry',
          action: message.action,
          employee_id: message.employee_id,
          data: message.data,
          timestamp: message.timestamp
        });
        break;
        
      case 'payroll':
        // Real-time payroll notification
        addNotification({
          type: 'payroll',
          action: message.action,
          payroll_run_id: message.payroll_run_id,
          data: message.data,
          timestamp: message.timestamp
        });
        break;
        
      case 'employee':
        // Real-time employee update
        addNotification({
          type: 'employee',
          action: message.action,
          employee_id: message.employee_id,
          timestamp: message.timestamp
        });
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };
  
  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 50)); // Keep last 50
  };
  
  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };
  
  const sendPing = () => {
    sendMessage({ type: 'ping' });
  };
  
  useEffect(() => {
    connect();
    
    // Ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(sendPing, 30000);
    
    return () => {
      clearInterval(pingInterval);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);
  
  return {
    isConnected,
    onlineUsers,
    notifications,
    sendMessage,
    clearNotifications: () => setNotifications([])
  };
};
