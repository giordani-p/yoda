import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, type Schemas } from "@/services/api/client";

const examplesKey = ["examples"];

export function useExamples() {
  return useQuery({
    queryKey: examplesKey,
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/examples");
      if (error) throw error;
      return data.items;
    },
  });
}

export function useCreateExample() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: Schemas["ExampleCreate"]) => {
      const { data, error } = await api.POST("/api/v1/examples", { body });
      if (error) throw error;
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: examplesKey }),
  });
}
