import { api } from "@/lib/axios";

import type { CreateUserValues, User } from "./types";

// Demo endpoint. Swap for a relative path (e.g. "/users") once the backend is
// wired up — the axios instance already prefixes NEXT_PUBLIC_API_BASE_URL and
// unwraps the { success, data, message } envelope.
const USERS_URL = "https://jsonplaceholder.typicode.com/users";

export function getUsers() {
  return api.get<User[]>(USERS_URL);
}

export function createUser(values: CreateUserValues) {
  return api.post<User>(USERS_URL, values);
}
