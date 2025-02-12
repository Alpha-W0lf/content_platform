// src/frontend/app/projects/[projectId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { projectsApi } from "@/lib/api";
import { ThemeToggle } from "@/components/theme-toggle";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { notFound } from 'next/navigation';
import { Project as ProjectSchema } from "@/types";

interface PageProps {
  params: {
    projectId: string;
  };
}

export default function ProjectDetailPage({ params }: PageProps) {
  const [project, setProject] = useState<ProjectSchema | null>(null);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProject = async () => {
      setLoading(true);
      setError(null);
      try {
        const projectData = await projectsApi.getProject(params.projectId);

        if (!projectData) {
          notFound(); // Correctly use the notFound function
        }

        setProject(projectData);
        setStatus(projectData.status);

      } catch (err: any) { // Use 'any' to handle different error types
          console.error("Failed to fetch project:", err);
          setError(err.message || "Failed to load project."); // Set a user-friendly error message

      } finally {
        setLoading(false);
      }
    };
    // Fetch the initial project status
        fetchProject();


    const pollStatus = setInterval(() => {
      projectsApi.getStatus(params.projectId)
        .then((data: any) => setStatus(data.status))
        .catch((err: any) => console.error("Failed to fetch project status:", err));
    }, 5000); // Good practice: Poll every 5 seconds

    // Clean up the interval when the component unmounts
    return () => clearInterval(pollStatus);
  }, [params.projectId]);  // Correct dependency array


  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!project) {
    return <div>Project not found</div>;  // This is a good fallback
  }

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold">Project Details</h1>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">
                {status}
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>
    </div>
  );
}
