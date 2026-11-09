import { Outlet } from "react-router";

export function AppLayout() {
  return (
    <>
      <header>
        <strong>Yoda</strong>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}
