import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type PropsWithChildren } from "react";

import { AuthTokenProvider } from "@/app/providers/auth-token-provider";
import { ThemeProvider } from "@/app/providers/theme-provider";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            staleTime: 30_000,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <ThemeProvider>
      <AuthTokenProvider>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </AuthTokenProvider>
    </ThemeProvider>
  );
}
