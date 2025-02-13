// src/frontend/app/projects/[projectId]/page.tsx
import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: { projectId: string } }): Promise<Metadata> {
    return {
        title: `Project ${params.projectId}`,
    }
}

export default async function ProjectPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  return (
    <div>
      <h1>Project ID: {projectId}</h1>
    </div>
  );
}
