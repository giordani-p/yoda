import { createBrowserRouter } from "react-router";

import { AppLayout } from "@/components/layout/AppLayout";
import { LoginPage } from "@/features/auth/LoginPage";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { UserMenu } from "@/features/auth/UserMenu";
import { ConversationView } from "@/features/conversations/ConversationView";
import {
  ConversationsLayout,
  NoConversationSelected,
} from "@/features/conversations/ConversationsLayout";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        path: "/",
        element: <AppLayout headerActions={<UserMenu />} />,
        children: [
          {
            element: <ConversationsLayout />,
            children: [
              { index: true, element: <NoConversationSelected /> },
              { path: "c/:conversationId", element: <ConversationView /> },
            ],
          },
        ],
      },
    ],
  },
]);
