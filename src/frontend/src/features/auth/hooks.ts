import { useQuery } from "@tanstack/react-query";

import { getMe } from "./api";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: getMe,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}
