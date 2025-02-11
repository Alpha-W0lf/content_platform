import { UserButton } from "@clerk/nextjs";
import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Content Platform</h1>
        <UserButton afterSignOutUrl="/"/>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Projects</h2>
          <Link 
            href="/projects"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            View All Projects
          </Link>
        </div>
        
        <p className="text-gray-600">
          Create and manage your content projects. Each project can contain multiple assets
          including scripts, narrations, videos, and more.
        </p>
      </div>
    </div>
  );
}