import type { ReactNode } from "react";
import { Outlet } from "react-router";

export function AppLayout({ headerActions }: { headerActions?: ReactNode }) {
  return (
    <>
      <header className="app-header">
        <strong>Yoda</strong>
        {headerActions}
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}
