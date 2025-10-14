import { Box, Input } from "@chakra-ui/react";
import { type SubmitHandler, useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { InputGroup } from "@/components/ui/input-group";
import type { YandexTokenCreate } from "@/client";

interface YandexTokenFormProps {
  onSubmit: SubmitHandler<YandexTokenCreate>;
  onDelete?: () => void;
  hasToken?: boolean;
}

export function YandexTokenForm({
  onSubmit,
  onDelete,
  hasToken,
}: YandexTokenFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<YandexTokenCreate>();

  return (
    <Box
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      display="flex"
      flexDirection="column"
      gap={4}
    >
      <Field invalid={!!errors.token} errorText={errors.token?.message}>
        <InputGroup w="100%">
          <Input
            {...register("token", { required: "Yandex API token is required" })}
            type="text"
            placeholder="Enter your Yandex API token"
          />
        </InputGroup>
      </Field>
      <Box display="flex" gap={4}>
        <Button type="submit" loading={isSubmitting}>
          {hasToken ? "Update Token" : "Save Token"}
        </Button>
        {hasToken && onDelete && (
          <Button
            type="button"
            variant="outline"
            colorScheme="red"
            onClick={onDelete}
          >
            Delete Token
          </Button>
        )}
      </Box>
    </Box>
  );
}
