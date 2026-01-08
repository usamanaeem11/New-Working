/**
 * Employees Hook
 * React hook for employee management
 */
import { useState, useEffect } from 'react';
import { apiClient } from '../utils/api-client';

export const useEmployees = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.getEmployees();
      setEmployees(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getEmployee = async (id) => {
    setLoading(true);
    try {
      return await apiClient.getEmployee(id);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const createEmployee = async (employeeData) => {
    setLoading(true);
    try {
      const newEmployee = await apiClient.createEmployee(employeeData);
      setEmployees([...employees, newEmployee]);
      return newEmployee;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  return {
    employees,
    loading,
    error,
    fetchEmployees,
    getEmployee,
    createEmployee,
  };
};
