import { createBrowserRouter } from "react-router";

import { AppLayout } from "@/components/layout/AppLayout";
import { ExamplesPage } from "@/features/example/ExamplesPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [{ index: true, element: <ExamplesPage /> }],
  },
]);
