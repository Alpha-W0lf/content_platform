import { Suspense, useEffect } from "react";
import { auth } from "@clerk/nextjs/server";
import ProjectDetails from "@/components/project-details";

export default function ProjectPage({
  params
}: {
  params: { projectId: string }
}) {
  // Ensure user is authenticated
  useEffect(() => {
    async function authenticate() {
      await auth();
    }
    authenticate();
  }, []);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProjectDetails projectId={params.projectId} />
    </Suspense>
  );
}
