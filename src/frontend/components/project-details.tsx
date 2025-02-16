"use client";

import { useEffect, useState } from "react";
import { projectsApi, ProjectSchema } from "@/lib/api";

interface ProjectDetailsProps {
  projectId: string;
}

export default function ProjectDetails({ projectId }: ProjectDetailsProps) {
  const [project, setProject] = useState<ProjectSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProject() {
      try {
        const data = await projectsApi.getProject(projectId);
        setProject(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load project');
      } finally {
        setLoading(false);
      }
    }

    loadProject();
  }, [projectId]);

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="mb-8">Loading project details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="mb-8 text-red-500">Error: {error}</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container mx-auto py-8">
        <div className="mb-8">Project not found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">{project.topic}</h1>
        <p className="text-muted-foreground mt-2">Status: {project.status}</p>
        {project.notes && (
          <div className="mt-4">
            <h2 className="text-xl font-semibold mb-2">Notes</h2>
            <p className="text-muted-foreground">{project.notes}</p>
          </div>
        )}
      </div>
    </div>
  );
}
