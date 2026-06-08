import { z } from "zod";

/** Shape returned by the users endpoint (demo uses jsonplaceholder). */
export interface User {
  id: number;
  name: string;
  username: string;
  email: string;
}

/** Validation schema for the create-user form (exercises every field type). */
export const createUserSchema = z.object({
  name: z.string().min(1, "Name is required"),
  username: z.string().min(3, "Username must be at least 3 characters"),
  email: z.email("Enter a valid email"),
  role: z.string().min(1, "Select a role"),
  plan: z.string().min(1, "Choose a plan"),
  bornAt: z.date({ error: "Pick a birth date" }),
  newsletter: z.boolean(),
});

export type CreateUserValues = z.infer<typeof createUserSchema>;
