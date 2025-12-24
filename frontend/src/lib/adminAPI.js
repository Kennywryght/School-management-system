import api from './api.js';

// Classes API
export const classesAPI = {
  getAll: async () => {
    const response = await api.get('/admin/classes');
    return response.data;
  },
  
  getOne: async (id) => {
    const response = await api.get(`/admin/classes/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/classes', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/admin/classes/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/classes/${id}`);
    return response.data;
  },
};

// Subjects API
export const subjectsAPI = {
  getAll: async () => {
    const response = await api.get('/admin/subjects');
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/subjects', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/admin/subjects/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/subjects/${id}`);
    return response.data;
  },
};

// Terms API
export const termsAPI = {
  getAll: async () => {
    const response = await api.get('/admin/terms');
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/terms', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/admin/terms/${id}`, data);
    return response.data;
  },
  
  activate: async (id) => {
    const response = await api.put(`/admin/terms/${id}/activate`);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/terms/${id}`);
    return response.data;
  },
};

// Teachers API
export const teachersAPI = {
  getAll: async () => {
    const response = await api.get('/admin/teachers');
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/teachers', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/admin/teachers/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/teachers/${id}`);
    return response.data;
  },
};

// Students API
export const studentsAPI = {
  getAll: async (classId = null) => {
    const url = classId ? `/admin/students?class_id=${classId}` : '/admin/students';
    const response = await api.get(url);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/students', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/admin/students/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/students/${id}`);
    return response.data;
  },
};

// Assignments API
export const assignmentsAPI = {
  getAll: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const url = params ? `/admin/assignments?${params}` : '/admin/assignments';
    const response = await api.get(url);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/admin/assignments', data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/admin/assignments/${id}`);
    return response.data;
  },
};