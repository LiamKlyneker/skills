import { useMutation, useQuery } from "@tanstack/react-query";
import { api, type ShelvesResponse } from "../api";

export function useShelves(teamId: string | undefined) {
  return useQuery<ShelvesResponse>({
    queryKey: ["shelves", teamId],
    queryFn: () => api.get(`/api/teams/${teamId}/shelves`),
    enabled: Boolean(teamId),
  });
}

export function useCreateShelf() {
  return useMutation({ mutationFn: (name: string) => api.post("/api/shelves", { name }) });
}

export function useArchiveShelf() {
  return useMutation({ mutationFn: (id: string) => api.post(`/api/shelves/${id}/archive`) });
}

export function useRestoreShelf() {
  return useMutation({ mutationFn: (id: string) => api.post(`/api/shelves/${id}/restore`) });
}

export function usePurgeShelf() {
  return useMutation({ mutationFn: (id: string) => api.delete(`/api/shelves/${id}`) });
}
