// Assignment Service
import { apiClient } from './api';

export interface Assignment {
  id: number;
  instructor_id: number;
  student_id: number;
  content_type: 'course' | 'deck';
  content_id: string;
  content_title: string;
  title: string;
  description: string;
  instructions: string;
  status: 'not_started' | 'in_progress' | 'completed';
  is_active: boolean;
  created_at: string;
}

export interface Progress {
  id: number;
  assignment_id: number;
  student_id: number;
  completion_percentage: number;
  time_spent: number;
  last_accessed: string;
  completed_at?: string;
  status: 'not_started' | 'in_progress' | 'completed';
}

export interface CreateAssignmentRequest {
  instructor_id: number;
  student_id: number;
  content_type: 'course' | 'deck';
  content_id: string;
  content_title: string;
  title: string;
  description: string;
  instructions: string;
}

export interface UpdateProgressRequest {
  completion_percentage: number;
  time_spent: number;
  status: 'not_started' | 'in_progress' | 'completed';
}

export const assignmentService = {
  // Assignments
  getAssignments: async (page: number = 1, size: number = 10): Promise<{
    assignments: Assignment[];
    total: number;
    page: number;
    size: number;
    total_pages: number;
  }> => {
    const response = await apiClient.get(`/api/assignments/?page=${page}&size=${size}`);
    return response.data;
  },

  getAssignment: async (assignmentId: number): Promise<Assignment> => {
    const response = await apiClient.get(`/api/assignments/${assignmentId}`);
    return response.data;
  },

  createAssignment: async (assignmentData: CreateAssignmentRequest): Promise<Assignment> => {
    const response = await apiClient.post('/api/assignments/', assignmentData);
    return response.data;
  },

  updateAssignment: async (assignmentId: number, assignmentData: Partial<CreateAssignmentRequest>): Promise<Assignment> => {
    const response = await apiClient.put(`/api/assignments/${assignmentId}`, assignmentData);
    return response.data;
  },

  deleteAssignment: async (assignmentId: number): Promise<void> => {
    await apiClient.delete(`/api/assignments/${assignmentId}`);
  },

  // Get assignments by instructor
  getInstructorAssignments: async (instructorId: number): Promise<Assignment[]> => {
    const response = await apiClient.get(`/api/assignments/instructors/${instructorId}`);
    return response.data;
  },

  // Get assignments by student
  getStudentAssignments: async (studentId: number): Promise<Assignment[]> => {
    const response = await apiClient.get(`/api/assignments/students/${studentId}`);
    return response.data;
  },

  // Progress
  getProgress: async (assignmentId: number): Promise<Progress> => {
    const response = await apiClient.get(`/api/progress/assignments/${assignmentId}`);
    return response.data;
  },

  updateProgress: async (assignmentId: number, progressData: UpdateProgressRequest): Promise<Progress> => {
    const response = await apiClient.put(`/api/progress/assignments/${assignmentId}`, progressData);
    return response.data;
  },

  getStudentProgress: async (studentId: number): Promise<Progress[]> => {
    const response = await apiClient.get(`/api/progress/students/${studentId}`);
    return response.data;
  },

  // Analytics
  getAnalyticsSummary: async (): Promise<{
    total_assignments: number;
    total_students: number;
    completion_rate: number;
    average_time_spent: number;
  }> => {
    const response = await apiClient.get('/api/analytics/summary');
    return response.data;
  },

  getStudentAnalytics: async (studentId: number): Promise<{
    total_assignments: number;
    completed_assignments: number;
    in_progress_assignments: number;
    average_completion_time: number;
    total_time_spent: number;
  }> => {
    const response = await apiClient.get(`/api/analytics/students/${studentId}`);
    return response.data;
  },

  getInstructorAnalytics: async (instructorId: number): Promise<{
    total_assignments_created: number;
    total_students: number;
    average_completion_rate: number;
    most_popular_content: any[];
  }> => {
    const response = await apiClient.get(`/api/analytics/instructors/${instructorId}`);
    return response.data;
  },
};
