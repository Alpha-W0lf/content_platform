'use client';

import { useEffect, useState } from 'react';
import { projectsApi, Project } from '@/lib/api';

export default function ProjectDetailPage({
  params: { projectId },
}: {
  params: { projectId: string };
}) {
  const [project, setProject] = useState<Project | null>(null);
  const [status, setStatus] = useState<string>('');

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const { status } = await projectsApi.getStatus(projectId);
        setStatus(status);
      } catch (error) {
        console.error('Failed to fetch project status:', error);
      }
    };

    const pollStatus = setInterval(fetchProject, 5000);
    fetchProject();

    return () => clearInterval(pollStatus);
  }, [projectId]);

  return (
    <div className="container mx-auto py-8">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Project Details</h1>
          <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-800">
            {status}
          </span>
        </div>

        {project && (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-medium">Name</h2>
              <p className="text-gray-600">{project.name}</p>
            </div>
            <div>
              <h2 className="text-lg font-medium">Topic</h2>
              <p className="text-gray-600">{project.topic}</p>
            </div>
            <div>
              <h2 className="text-lg font-medium">Created At</h2>
              <p className="text-gray-600">
                {new Date(project.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}