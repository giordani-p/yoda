import { Outlet } from "react-router";

export function AppLayout() {
  return (
    <>
      <header>
        <strong>my-project</strong>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}
