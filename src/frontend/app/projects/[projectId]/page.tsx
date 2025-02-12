// src/frontend/app/projects/[projectId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { projectsApi } from "@/lib/api"; // Import the corrected type
import { ThemeToggle } from "@/components/theme-toggle";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { notFound } from 'next/navigation'; // Import notFound
import { Project as ProjectSchema } from "@/types";

interface PageProps {
  params: {
    projectId: string;
  };
}

export default function ProjectDetailPage({ params }: PageProps) {
  const [project, setProject] = useState<ProjectSchema | null>(null);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(true); // Add a loading state
  const [error, setError] = useState<string | null>(null); // Add an error state

  useEffect(() => {
    const fetchProject = async () => {
      setLoading(true); // Set loading to true before fetching
      setError(null);    // Clear any previous errors
      try {
        const projectData = await projectsApi.getProject(params.projectId);

        if (!projectData) {
          notFound(); // Use Next.js notFound helper
        }

        setProject(projectData);
        setStatus(projectData.status);

      } catch (err:any) { //use any type for error
          console.error("Failed to fetch project:", err);
          setError(err.message || "Failed to load project."); // Provide a user-friendly error

      } finally {
        setLoading(false); // Set loading to false after fetching
      }
    };

    const pollStatus = setInterval(() => {
      projectsApi.getStatus(params.projectId)
        .then(data => setStatus(data.status))
        .catch(err => console.error("Failed to fetch project status:", err));
    }, 5000);

      fetchProject();
      return () => clearInterval(pollStatus);
  }, [params.projectId]);


  if (loading) {
    return <div>Loading...</div>; // Display a loading message
  }

  if (error) {
    return <div>Error: {error}</div>; // Display an error message
  }

  if (!project) {
    return <div>Project not found</div>; // Should not happen due to notFound, but good to have
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
