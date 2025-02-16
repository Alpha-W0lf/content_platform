# All tasks completed for this guide.

# Progress Tracker

- [x] ThemeProvider Setup
- [x] globals.css Configuration
- [x] Shadcn/ui Component Installation
- [x] Shadcn/ui Component Usage
- [x] Theme Toggle

---

user prompt:
lets switch gears. i want to make sure we use a dark theme and also shadcn/ui. should we make sure these are implemented pretty early on?

response:
Yes, absolutely. Implementing the dark theme and using shadcn/ui components should be done very early in the frontend development process. Here's why, and how to approach it:

Why Early Implementation is Important:

Consistency: Starting with your desired theme (dark) and UI component library (shadcn/ui) ensures visual consistency from the beginning. It's much harder to retrofit a theme or component library later.

Reduced Rework: If you build a significant portion of your UI with default styling or a different component library and then try to switch to a dark theme and shadcn/ui, you'll face a lot of tedious rework:

You'll have to manually update the styling of every component.

You might encounter unexpected conflicts or styling issues.

You'll likely need to rewrite parts of your components to use shadcn/ui's API.

Developer Experience: It's simply more pleasant and efficient to develop with the final styles and components in place. You get immediate visual feedback and can catch styling issues early.

Shadcn/ui's Approach: Shadcn/ui is not a traditional component library that you install as a single package. It's a collection of copy-and-paste components that you add to your project. This means you have full control over the code, but it also means you need to integrate them from the start.

Component Planning: Using shadcn/ui early helps ensure that we carefully plan for the specific components needed for the project.

How to Implement Early:

ThemeProvider (Already Done): You've already done the most important step: You've included the ThemeProvider in your src/frontend/app/layout.tsx:

import { ClerkProvider } from "@clerk/nextjs";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider"; // <--- This
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>
          <ThemeProvider // <--- This
            attribute="class"
            defaultTheme="dark" // <---  Set dark as default
            enableSystem
            disableTransitionOnChange
          >
            <main className="min-h-screen bg-background">{children}</main>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
content_copy
download
Use code with caution.
TypeScript

defaultTheme="dark": This is the key setting. It ensures that your application defaults to dark mode.

attribute="class": This tells next-themes to use the class attribute (i.e., dark class on the <html> element) to manage the theme. This works seamlessly with Tailwind CSS.

enableSystem: This allows the user's system preference (light or dark mode) to be used if they haven't explicitly chosen a theme.

bg-background and text-foreground: Notice the Tailwind classes applied, which are using colors set in the dark theme.

globals.css (Already Done): You've already configured your globals.css with the correct CSS variables for both light and dark themes, and you're using Tailwind's dark: variant correctly. This is perfect.

Shadcn/ui Components (Start Now):

Installation (Mostly Done): You've already installed shadcn-ui and many of its dependencies.

Component Usage: From this point forward, use shadcn/ui components for all your UI elements. Don't use plain HTML elements or build your own components unless absolutely necessary. For example, instead of:

<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Click Me
</button>
content_copy
download
Use code with caution.
TypeScript

Use:

import { Button } from "@/components/ui/button"

<Button>Click Me</Button>
content_copy
download
Use code with caution.
TypeScript

Add Components As Needed: Use the npx shadcn-ui@latest add <component-name> command to add components as you need them. For example:

npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
# ... and so on
content_copy
download
Use code with caution.
Bash

This will copy the component's code into your src/frontend/components/ui directory.

Customization: The beauty of shadcn/ui is that you can customize the components directly. Since the code is in your project, you can modify the styles, functionality, and even the underlying Radix UI primitives. However, start by using the default styles and only customize when necessary.

Theme Toggle (Already Done): You've already included the ThemeToggle component, which allows users to switch between light and dark mode. This is great for testing and providing user choice.

Example (Putting it Together):

Let's say you're building the project creation form in src/frontend/app/projects/page.tsx. Instead of using plain HTML inputs and buttons, use the shadcn/ui equivalents:

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { projectsApi, Project } from "@/lib/api";
import { Button } from "@/components/ui/button"; // Import shadcn/ui components
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";

export default function ProjectsPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState(""); // Use notes
  const [projects, setProjects] = useState<Project[]>([]);

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

      {isCreating &amp;&amp; (
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
content_copy
download
Use code with caution.
TypeScript

Notice how:

We're importing Button, Input, Label, Card, CardHeader, CardContent, and CardFooter from @/components/ui.

We're using these components instead of plain HTML elements.

We're still using Tailwind classes for layout and spacing (e.g., container, mx-auto, py-8, space-y-4), but the components themselves are styled by shadcn/ui.

The dark theme is automatically applied because of the ThemeProvider and the CSS variables in globals.css.

By following this pattern consistently, you'll build a visually consistent and maintainable UI with minimal effort. And because you're starting this way, you won't have to go back and refactor your frontend later.
