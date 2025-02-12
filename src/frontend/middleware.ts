import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: ["/health", "/(auth)/sign-in/[[...sign-in]]", "/(auth)/sign-up/[[...sign-up]]", "/", "/projects(.*)"],
});

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
