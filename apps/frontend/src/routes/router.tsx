import { createBrowserRouter } from "react-router";

import { AppLayout } from "@/components/layout/AppLayout";
import { LoginPage } from "@/features/auth/LoginPage";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { UserMenu } from "@/features/auth/UserMenu";
import { ExamplesPage } from "@/features/example/ExamplesPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        path: "/",
        element: <AppLayout headerActions={<UserMenu />} />,
        children: [{ index: true, element: <ExamplesPage /> }],
      },
    ],
  },
]);
