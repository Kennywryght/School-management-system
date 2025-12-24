import api from './api.js';

// Teacher endpoints
export const teacherAPI = {
  // Get my assignments
  getMyAssignments: async (termId = null) => {
    const url = termId ? `/teacher/my-assignments?term_id=${termId}` : '/teacher/my-assignments';
    const response = await api.get(url);
    return response.data;
  },
  
  // Get students in a class
  getStudentsInClass: async (classId) => {
    const response = await api.get(`/teacher/classes/${classId}/students`);
    return response.data;
  },
  
  // Upload single result
  uploadResult: async (data) => {
    const response = await api.post('/teacher/results', data);
    return response.data;
  },
  
  // Upload bulk results
  uploadBulkResults: async (data) => {
    const response = await api.post('/teacher/results/bulk', data);
    return response.data;
  },
  
  // Get my uploaded results
  getMyResults: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `/teacher/results?${params}` : '/teacher/results';
    const response = await api.get(url);
    return response.data;
  },
  
  // Update result
  updateResult: async (id, data) => {
    const response = await api.put(`/teacher/results/${id}`, data);
    return response.data;
  },
};