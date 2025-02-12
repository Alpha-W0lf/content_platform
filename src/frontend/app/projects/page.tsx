"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { projectsApi, Project } from "@/lib/api";

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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Projects</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
        >
          Create New Project
        </button>
      </div>

      {isCreating && (
        <form
          onSubmit={handleCreateProject}
          className="bg-white shadow rounded-lg p-6 mb-8"
        >
          <div className="space-y-4">
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700"
              >
                Project Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label
                htmlFor="topic"
                className="block text-sm font-medium text-gray-700"
              >
                Topic
              </label>
              <input
                type="text"
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </div>
        </form>
      )}

      <div className="bg-white shadow rounded-lg">
        <ul className="divide-y divide-gray-200">
          {projects.map((project) => (
            <li
              key={project.id}
              className="p-4 hover:bg-gray-50 cursor-pointer"
              onClick={() => router.push(`/projects/${project.id}`)}
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Topic: {project.topic}
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="px-2 py-1 text-sm rounded-full bg-blue-100 text-blue-800">
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
