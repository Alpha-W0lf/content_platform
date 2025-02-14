import { UserButton } from "@clerk/nextjs";
import { ThemeToggle } from "../components/theme-toggle";
import Link from "next/link";
import { Card, CardHeader, CardContent } from "../components/ui/card";
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Content Platform</h1>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <UserButton afterSignOutUrl="/" />
        </div>
      </div>

      <Card>
          <CardHeader>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Projects</h2>
              <Link
                href="/projects"
                className="rounded bg-primary px-4 py-2 text-primary-foreground transition-colors hover:bg-primary/90"
              >
                View All Projects
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Create and manage your content projects. Each project can contain
              multiple assets including scripts, narrations, videos, and more.
            </p>
          </CardContent>
        </Card>

      <div className="flex gap-4 mt-8">
        <Button>Default Button</Button>
        <Button variant="destructive">Destructive Button</Button>
        <Button variant="outline">Outline Button</Button>
        <Button variant="secondary">Secondary Button</Button>
        <Button variant="ghost">Ghost Button</Button>
        <Button variant="link">Link Button</Button>
      </div>
    </div>
  );
}
