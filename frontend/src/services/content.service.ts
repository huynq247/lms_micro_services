// Content Service
import { apiClient } from './api';

export interface Course {
  id: string;
  title: string;
  description: string;
  instructor_id: string;
  is_active: boolean;
  lessons: Lesson[];
  created_at: string;
  updated_at: string;
}

export interface Lesson {
  id: string;
  course_id: string;
  title: string;
  content: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
}

export interface Deck {
  id: string;
  title: string;
  description: string;
  instructor_id: string;
  instructor_name?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  is_active: boolean;
  is_public: boolean;
  is_published?: boolean; // Backend field
  flashcards?: Flashcard[];
  total_flashcards?: number;
  created_at: string;
  updated_at?: string;
}

export interface Flashcard {
  id: string;
  deck_id: string;
  front: string;
  back: string;
  order: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  front_image_url?: string;
  back_image_url?: string;
  is_active?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateCourseRequest {
  title: string;
  description: string;
  instructor_id: string;
}

export interface CreateLessonRequest {
  course_id: string;
  title: string;
  content: string;
  order_index: number;
}

export interface CreateDeckRequest {
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  instructor_id: string;
  is_public?: boolean;
}

export interface CreateFlashcardRequest {
  deck_id: string;
  front: string;
  back: string;
  order: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  front_image_url?: string;
  back_image_url?: string;
}

export const contentService = {
  // Courses
  getCourses: async (): Promise<{ courses: Course[] }> => {
    const response = await apiClient.get('/api/courses/');
    return response.data;
  },

  getCourse: async (courseId: string): Promise<Course> => {
    const response = await apiClient.get(`/api/courses/${courseId}`);
    return response.data;
  },

  createCourse: async (courseData: CreateCourseRequest): Promise<Course> => {
    const response = await apiClient.post('/api/courses/', courseData);
    return response.data;
  },

  updateCourse: async (courseId: string, courseData: Partial<CreateCourseRequest>): Promise<Course> => {
    const response = await apiClient.put(`/api/courses/${courseId}`, courseData);
    return response.data;
  },

  deleteCourse: async (courseId: string): Promise<void> => {
    await apiClient.delete(`/api/courses/${courseId}`);
  },

  // Lessons
  getLessons: async (courseId: string): Promise<{ lessons: Lesson[] }> => {
    const response = await apiClient.get(`/api/courses/${courseId}/lessons`);
    return response.data;
  },

  createLesson: async (lessonData: CreateLessonRequest): Promise<Lesson> => {
    const response = await apiClient.post('/api/lessons/', lessonData);
    return response.data;
  },

  updateLesson: async (lessonId: string, lessonData: Partial<CreateLessonRequest>): Promise<Lesson> => {
    const response = await apiClient.put(`/api/lessons/${lessonId}`, lessonData);
    return response.data;
  },

  deleteLesson: async (lessonId: string): Promise<void> => {
    await apiClient.delete(`/api/lessons/${lessonId}`);
  },

  // Decks
  getDecks: async (): Promise<{ decks: Deck[] }> => {
    const response = await apiClient.get('/api/decks/');
    // Map API response structure (items) to expected frontend structure (decks)
    return {
      decks: response.data.items || []
    };
  },

  getDeck: async (deckId: string): Promise<Deck> => {
    const response = await apiClient.get(`/api/decks/${deckId}`);
    return response.data;
  },

  createDeck: async (deckData: CreateDeckRequest): Promise<Deck> => {
    const response = await apiClient.post('/api/decks/', deckData);
    return response.data;
  },

  updateDeck: async (deckId: string, deckData: Partial<CreateDeckRequest>): Promise<Deck> => {
    const response = await apiClient.put(`/api/decks/${deckId}`, deckData);
    return response.data;
  },

  deleteDeck: async (deckId: string): Promise<void> => {
    await apiClient.delete(`/api/decks/${deckId}`);
  },

  // Flashcards
  getFlashcards: async (deckId: string): Promise<{ flashcards: Flashcard[] }> => {
    const response = await apiClient.get(`/api/decks/${deckId}/flashcards`);
    return response.data;
  },

  createFlashcard: async (flashcardData: CreateFlashcardRequest): Promise<Flashcard> => {
    const response = await apiClient.post(`/api/decks/${flashcardData.deck_id}/flashcards`, flashcardData);
    return response.data;
  },

  updateFlashcard: async (flashcardId: string, flashcardData: Partial<CreateFlashcardRequest>): Promise<Flashcard> => {
    const response = await apiClient.put(`/api/decks/flashcards/${flashcardId}`, flashcardData);
    return response.data;
  },

  deleteFlashcard: async (flashcardId: string): Promise<void> => {
    await apiClient.delete(`/api/decks/flashcards/${flashcardId}`);
  },
};
