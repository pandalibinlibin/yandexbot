import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UsersService, YandexTokenCreate } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { YandexTokenForm } from "./YandexTokenForm";

export function YandexTokenSettings() {
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const queryClient = useQueryClient();

  const { data: token, isLoading } = useQuery({
    queryKey: ["yandex-token"],
    queryFn: () => UsersService.readUserYandexToken(),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: (data: YandexTokenCreate) =>
      UsersService.createUserYandexToken({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["yandex-token"] });
      showSuccessToast("Yandex token has been saved");
    },
    onError: () => {
      showErrorToast("Failed to save Yandex token");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => UsersService.deleteUserYandexToken(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["yandex-token"] });
      showSuccessToast("Yandex token has been deleted");
    },
    onError: () => {
      showErrorToast("Failed to delete Yandex token");
    },
  });

  if (isLoading) {
    return null;
  }

  return (
    <YandexTokenForm
      onSubmit={createMutation.mutate}
      onDelete={deleteMutation.mutate}
      hasToken={!!token}
    />
  );
}
