// src/frontend/lib/api.ts
import axios from 'axios';
import type { Project, ProjectCreate, ProjectStatus } from "../types";

const getApiUrl = () => {
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  } else {
    return '';
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
        return response.data;
    },
    getProject: async (projectId: string): Promise<Project> => {
        const response = await api.get(`/projects/${projectId}`);
        return response.data;
    }
};

export type { Project as ProjectSchema, ProjectCreate, ProjectStatus };
