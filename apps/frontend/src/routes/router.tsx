import { createBrowserRouter } from "react-router";

import { AppLayout } from "@/components/layout/AppLayout";
import { ChatPage } from "@/features/assistant/ChatPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { UserMenu } from "@/features/auth/UserMenu";
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
              { path: "c/:conversationId", element: <ChatPage /> },
            ],
          },
        ],
      },
    ],
  },
]);
