import { api } from "@/lib/axios";

import type { AuthToken, AuthUser, LoginValues, RegisterValues } from "./types";

export function login(data: LoginValues) {
  return api.post<AuthToken>("/auth/login", data);
}

export function register(data: RegisterValues) {
  return api.post<AuthUser>("/auth/register", data);
}

export function getMe() {
  return api.get<AuthUser>("/users/me");
}
