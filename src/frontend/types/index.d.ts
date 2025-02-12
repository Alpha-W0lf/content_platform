// src/frontend/types/index.d.ts
export interface Project {
    id: string;
    name: string | null;
    topic: string;
    status: string;
    created_at: string;
    updated_at: string;
    notes?: string;
  }

  export interface ProjectCreate {
    topic: string;
    notes?: string;
  }

  export interface ProjectStatus {
      status: string;
  }