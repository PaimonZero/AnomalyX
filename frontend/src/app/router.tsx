import { createBrowserRouter, Navigate } from "react-router-dom";

import { ApiTestingPage } from "@/features/api-testing/pages/api-testing-page";
import { AlertsPage } from "@/features/alerts/pages/alerts-page";
import { BatchScoringPage } from "@/features/batch-scoring/pages/batch-scoring-page";
import { MonitoringPage } from "@/features/monitoring/pages/monitoring-page";
import { AppShell } from "@/layouts/app-shell";
import { NotFoundPage } from "@/shared/ui/not-found-page";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/alerts" replace /> },
      { path: "alerts", element: <AlertsPage /> },
      { path: "api-testing", element: <ApiTestingPage /> },
      { path: "batch-scoring", element: <BatchScoringPage /> },
      { path: "monitoring", element: <MonitoringPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
