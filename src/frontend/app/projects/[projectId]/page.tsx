"use client";

import { useEffect, useState } from "react";
import { projectsApi } from "../../../lib/api"; // Correct relative import
import { ThemeToggle } from "../../../components/theme-toggle"; // Correct relative import
import { Card, CardHeader, CardContent } from "../../../components/ui/card";
import { notFound } from 'next/navigation';
import type { Project } from "../../../types"; // Import Project

// Corrected Interface:  params MUST be strings.
interface PageProps {
    params: {
        projectId: string;
    };
}

export default function ProjectDetailPage({ params }: PageProps) {
    const [project, setProject] = useState<Project | null>(null); // Use the correct type here
    const [status, setStatus] = useState<string>(""); // and a separate state for status
    const [loading, setLoading] = useState(true);  // Add a loading state!
    const [error, setError] = useState<string | null>(null); // Add error state


    useEffect(() => {
        const fetchProject = async () => {
            setLoading(true); // Set loading to true before the API call
            setError(null);   //Reset error

            try {
                const projectData = await projectsApi.getProject(params.projectId);
                 if (!projectData) {
                    notFound(); //this is correct
                  }
                  setProject(projectData);
                  setStatus(projectData.status);
            } catch (err: any) {  //  Use 'any' to handle different error types
                console.error("Failed to fetch project:", err);
                setError(err.message || "Failed to load project."); // Use generic message
              } finally {
                  setLoading(false); // Always set loading to false, even on error
              }
        };

        fetchProject();

        const pollStatus = setInterval(() => {
            projectsApi.getStatus(params.projectId)
            .then(data => setStatus(data.status)) // No need for :any, the types are correct.
            .catch(err => console.error("Failed to fetch project status:", err));
        }, 5000);

        return () => clearInterval(pollStatus); // Clean up the interval!
    }, [params.projectId]);  // Correct dependency array


    if (loading) {
        return <div>Loading...</div>; // Show loading indicator
    }

    if (error) {
      return <div>Error: {error}</div>; // Show error message
    }

    if (!project) {
        return <div>Project not found</div>; // Redundant, but good for clarity
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
