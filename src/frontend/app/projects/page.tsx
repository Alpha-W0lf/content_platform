"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { projectsApi, Project } from "@/lib/api";
import { ThemeToggle } from "@/components/theme-toggle";

export default function ProjectsPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const [topic, setTopic] = useState("");
  const [name, setName] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await projectsApi.create({ name, topic });
      setProjects([...projects, project]);
      setTopic("");
      setName("");
      setIsCreating(false);
    } catch (error) {
      console.error("Failed to create project:", error);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Projects</h1>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <button
            onClick={() => setIsCreating(true)}
            className="rounded bg-primary px-4 py-2 text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Create New Project
          </button>
        </div>
      </div>

      {isCreating && (
        <form
          onSubmit={handleCreateProject}
          className="mb-8 rounded-lg bg-card p-6 shadow"
        >
          <div className="space-y-4">
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-foreground"
              >
                Project Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                required
              />
            </div>
            <div>
              <label
                htmlFor="topic"
                className="block text-sm font-medium text-foreground"
              >
                Topic
              </label>
              <input
                type="text"
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                required
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-accent hover:text-accent-foreground"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90"
              >
                Create
              </button>
            </div>
          </div>
        </form>
      )}

      <div className="rounded-lg bg-card shadow">
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
      </div>
    </div>
  );
}
