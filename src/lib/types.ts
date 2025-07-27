import { z } from 'zod';

// Input validation schemas
export const createProjectSchema = z.object({
  projectName: z
    .string()
    .min(1, 'Project name is required')
    .max(30, 'Project name must be 30 characters or less')
    .regex(/^[a-z][a-z0-9-]*$/, 'Project name must start with a letter and contain only lowercase letters, numbers, and hyphens'),
  orgDomain: z.string()
    .min(1, 'Organization domain is required')
    .regex(/^[a-z][a-z0-9-]*$/, 'Organization domain must start with a letter and contain only lowercase letters, numbers, and hyphens'),
  templateRepo: z.string()
    .min(1, 'Template repository is required')
    .regex(/^[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+$/, 'Template repository must be in format: username/repository'),
  templateBranch: z.string()
    .min(1, 'Template branch is required'),
  firebaseAccount: z.string()
    .email('Firebase account must be a valid email address')
    .min(1, 'Firebase account is required')
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>; 