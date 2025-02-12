"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { projectsApi, ProjectSchema } from "../../lib/api";
import { ThemeToggle } from "../../components/theme-toggle";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Card, CardHeader, CardContent, CardFooter } from "../../components/ui/card";

export default function ProjectsPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState(""); // Use notes
  const [projects, setProjects] = useState<ProjectSchema[]>([]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await projectsApi.create({ topic, notes }); // Pass notes
      setProjects([...projects, project]);
      setTopic("");
      setNotes(""); // Clear notes
      setIsCreating(false);
    } catch (error) {
      console.error("Failed to create project:", error);
      // Add error handling (e.g., show a toast notification)
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Projects</h1>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Button onClick={() => setIsCreating(true)}>
            Create New Project
          </Button>
        </div>
      </div>

      {isCreating && (
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Create Project</h2>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <Label htmlFor="topic">Topic</Label>
                  <Input
                    type="text"
                    id="topic"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <Input
                    type="text"
                    id="notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>
              </form>
            </CardContent>
            <CardFooter>
             <div className="flex justify-end space-x-3">
                <Button variant="outline" onClick={() => setIsCreating(false)}>
                  Cancel
                </Button>
                <Button type="submit">Create</Button>
             </div>
            </CardFooter>
          </Card>
        )}

        <Card>
          <ul className="divide-y divide-border">
            {projects.map((project) => (
              <li
                key={project.id}
                className="cursor-pointer p-4 hover:bg-accent hover:text-accent-foreground"
                onClick={() => router.push(`/projects/${project.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium">
                      {project.name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Topic: {project.topic}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="rounded-full bg-primary/10 px-2 py-1 text-sm text-primary">
                      {project.status}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </Card>
    </div>
  );
}
