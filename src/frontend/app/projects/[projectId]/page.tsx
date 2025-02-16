import { Suspense } from "react";
import { auth } from "@clerk/nextjs/server";
import ProjectDetails from "@/components/project-details";

export default async function ProjectPage({ params }: { params: { projectId: string } }) {
  const { userId } = await auth();

  if (!userId) {
    return null; // Or your preferred handling
  }

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProjectDetails projectId={params.projectId} />
    </Suspense>
  );
}
