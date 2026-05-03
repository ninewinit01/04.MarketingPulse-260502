import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./api";
import type {
  CollectionRun,
  ContentItem,
  CuratedChannel,
  DashboardResponse,
  Industry,
  Keyword,
  Paginated,
  Source,
} from "@/types/api";

// ───────── Public ─────────

export function useDashboard(date: string, industry?: string) {
  return useQuery({
    queryKey: ["dashboard", date, industry ?? ""],
    queryFn: async () => {
      const { data } = await api.get<DashboardResponse>("/dashboard/", {
        params: { date, industry },
      });
      return data;
    },
  });
}

export function usePublicIndustries() {
  return useQuery({
    queryKey: ["public-industries"],
    queryFn: async () => {
      const { data } = await api.get<Industry[]>("/industries/");
      return data;
    },
    staleTime: 5 * 60_000,
  });
}

export function useContentList(filters: { date?: string; industry?: string; source?: string }) {
  return useQuery({
    queryKey: ["content", filters],
    queryFn: async () => {
      const { data } = await api.get<Paginated<ContentItem>>("/content/", { params: filters });
      return data;
    },
  });
}

// ───────── Admin: Industries ─────────

export function useAdminIndustries() {
  return useQuery({
    queryKey: ["admin-industries"],
    queryFn: async () => {
      const { data } = await api.get<Industry[]>("/admin/industries/");
      return data;
    },
  });
}

export function useCreateIndustry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Industry>) => {
      const { data } = await api.post<Industry>("/admin/industries/", payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-industries"] }),
  });
}

export function useUpdateIndustry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Industry> & { id: number }) => {
      const { data } = await api.patch<Industry>(`/admin/industries/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-industries"] }),
  });
}

export function useDeleteIndustry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/admin/industries/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-industries"] }),
  });
}

// ───────── Admin: Keywords ─────────

export function useAdminKeywords(industryId?: number) {
  return useQuery({
    queryKey: ["admin-keywords", industryId ?? "all"],
    queryFn: async () => {
      const { data } = await api.get<Keyword[]>("/admin/keywords/", {
        params: industryId ? { industry: industryId } : {},
      });
      return data;
    },
  });
}

export function useCreateKeyword() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Keyword>) => {
      const { data } = await api.post<Keyword>("/admin/keywords/", payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-keywords"] }),
  });
}

export function useUpdateKeyword() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Keyword> & { id: number }) => {
      const { data } = await api.patch<Keyword>(`/admin/keywords/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-keywords"] }),
  });
}

export function useDeleteKeyword() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/admin/keywords/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-keywords"] }),
  });
}

// ───────── Admin: Sources ─────────

export function useAdminSources() {
  return useQuery({
    queryKey: ["admin-sources"],
    queryFn: async () => {
      const { data } = await api.get<Source[]>("/admin/sources/");
      return data;
    },
  });
}

export function useUpdateSource() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Source> & { id: number }) => {
      const { data } = await api.patch<Source>(`/admin/sources/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-sources"] }),
  });
}

// ───────── Admin: Curated YouTube Channels ─────────

export function useAdminChannels() {
  return useQuery({
    queryKey: ["admin-channels"],
    queryFn: async () => {
      const { data } = await api.get<CuratedChannel[]>("/admin/channels/");
      return data;
    },
  });
}

export function useCreateChannel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<CuratedChannel>) => {
      const { data } = await api.post<CuratedChannel>("/admin/channels/", payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-channels"] }),
  });
}

export function useUpdateChannel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<CuratedChannel> & { id: number }) => {
      const { data } = await api.patch<CuratedChannel>(`/admin/channels/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-channels"] }),
  });
}

export function useDeleteChannel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/admin/channels/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-channels"] }),
  });
}

// ───────── Admin: Runs ─────────

export function useAdminRuns() {
  return useQuery({
    queryKey: ["admin-runs"],
    queryFn: async () => {
      const { data } = await api.get<Paginated<CollectionRun> | CollectionRun[]>(
        "/admin/runs/",
      );
      return Array.isArray(data) ? data : data.results;
    },
    refetchInterval: 5_000,
  });
}

export function useTriggerRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post<{ status: string }>("/admin/runs/trigger/");
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-runs"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
