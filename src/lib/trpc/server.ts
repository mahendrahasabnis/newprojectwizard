import { initTRPC } from '@trpc/server';
import { createProjectSchema } from '@/lib/types';

const t = initTRPC.create();

export const router = t.router;
export const publicProcedure = t.procedure;

// Re-export types for server use
export { createProjectSchema };
export type { CreateProjectInput } from '@/lib/types';

// Main router
export const appRouter = router({
  createProject: publicProcedure
    .input(createProjectSchema)
    .mutation(async ({ input }) => {
      // This will be implemented in the API route
      return { success: true, projectName: input.projectName };
    }),
});

export type AppRouter = typeof appRouter; 