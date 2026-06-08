/**
 * Standard response envelope returned by every backend endpoint.
 *
 * @see project memory "api-response-envelope"
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

/** Narrow an unknown response body to the {@link ApiResponse} envelope. */
export function isApiResponse<T>(body: unknown): body is ApiResponse<T> {
  return (
    typeof body === "object" &&
    body !== null &&
    "success" in body &&
    "data" in body &&
    "message" in body
  );
}
