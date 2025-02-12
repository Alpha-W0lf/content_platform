"use client";

import { useEffect, useState } from "react";
import { projectsApi, Project } from "@/lib/api";
import { ThemeToggle } from "@/components/theme-toggle";

export default function ProjectDetailPage({
  params: { projectId },
}: {
  params: { projectId: string };
}) {
  const [project, setProject] = useState<Project | null>(null);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const { status } = await projectsApi.getStatus(projectId);
        setStatus(status);
      } catch (error) {
        console.error("Failed to fetch project status:", error);
      }
    };

    const pollStatus = setInterval(fetchProject, 5000);
    fetchProject();

    return () => clearInterval(pollStatus);
  }, [projectId]);

  return (
    <div className="container mx-auto py-8">
      <div className="rounded-lg bg-card p-6 shadow">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Project Details</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">
              {status}
            </span>
          </div>
        </div>

        {project && (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-medium">Name</h2>
              <p className="text-muted-foreground">{project.name}</p>
            </div>
            <div>
              <h2 className="text-lg font-medium">Topic</h2>
              <p className="text-muted-foreground">{project.topic}</p>
            </div>
            <div>
              <h2 className="text-lg font-medium">Created At</h2>
              <p className="text-muted-foreground">
                {new Date(project.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
