import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
} from "axios";

import { type ApiResponse, isApiResponse } from "./api-response";
import { getToken } from "./auth";

/**
 * Shared axios instance. Point it at the backend gateway via
 * `NEXT_PUBLIC_API_BASE_URL` (see `.env.example`).
 */
export const http: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

http.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/** Pull a human-readable message out of an axios error. */
function toErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const body = error.response?.data;
    if (isApiResponse(body) && body.message) return body.message;
    return error.message;
  }
  return error instanceof Error ? error.message : "Unexpected error";
}

/**
 * Issue a request and unwrap the `{ success, data, message }` envelope,
 * returning `data` directly. Bodies that are not enveloped (e.g. third-party
 * APIs) are returned as-is so the same client works everywhere.
 */
export async function apiRequest<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await http.request<ApiResponse<T> | T>(config);
    const body = response.data;

    if (isApiResponse<T>(body)) {
      if (!body.success) throw new Error(body.message || "Request failed");
      return body.data;
    }

    return body as T;
  } catch (error) {
    throw new Error(toErrorMessage(error));
  }
}

/** Thin typed helpers over {@link apiRequest}. */
export const api = {
  get: <T>(url: string, config?: AxiosRequestConfig) =>
    apiRequest<T>({ ...config, method: "GET", url }),
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiRequest<T>({ ...config, method: "POST", url, data }),
  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiRequest<T>({ ...config, method: "PUT", url, data }),
  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiRequest<T>({ ...config, method: "PATCH", url, data }),
  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    apiRequest<T>({ ...config, method: "DELETE", url }),
};
