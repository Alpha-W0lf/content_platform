// src/frontend/lib/api.ts
import axios from 'axios';
import type { ProjectCreate, Project, ProjectStatus } from "../types"; // Import using the correct type definition


const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side (Next.js API routes, etc.) - use the environment variable, with a fallback to localhost
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  } else {
    // Client-side - assume same origin (works if frontend is served from Next.js dev server)
    return ''; // Empty string uses the current origin
  }
};
const api = axios.create({
    baseURL: getApiUrl(),
});

export const projectsApi = {
    create: async (data: ProjectCreate): Promise<Project> => {
        const response = await api.post('/projects/', data);
        return response.data;
    },
    getStatus: async (projectId: string): Promise<ProjectStatus> => {
        const response = await api.get(`/projects/${projectId}/status`);
        return response.data
    },
    // Add get project by id endpoint
    getProject: async (projectId: string): Promise<Project> => {
        const response = await api.get(`/projects/${projectId}`);
        return response.data
    }
}

export type { ProjectCreate, Project, ProjectStatus };
