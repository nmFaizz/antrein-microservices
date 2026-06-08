const TOKEN_KEY = "auth_token";
const ROLE_KEY = "user_role";
const MAX_AGE = 60 * 60 * 24 * 7; // 7 days

export function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${TOKEN_KEY}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function setToken(token: string): void {
  document.cookie = `${TOKEN_KEY}=${encodeURIComponent(token)}; path=/; max-age=${MAX_AGE}; SameSite=Lax`;
}

export function getRole(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${ROLE_KEY}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function setRole(role: string): void {
  document.cookie = `${ROLE_KEY}=${encodeURIComponent(role)}; path=/; max-age=${MAX_AGE}; SameSite=Lax`;
}

export function clearToken(): void {
  document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
  document.cookie = `${ROLE_KEY}=; path=/; max-age=0`;
}
