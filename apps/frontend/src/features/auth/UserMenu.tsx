import { useNavigate } from "react-router";

import { useCurrentUser, useLogout } from "./api";

export function UserMenu() {
  const currentUser = useCurrentUser();
  const logout = useLogout();
  const navigate = useNavigate();

  function handleLogout() {
    logout.mutate(undefined, {
      onSuccess: () => navigate("/login", { replace: true }),
    });
  }

  return (
    <div className="user-menu">
      <span>{currentUser.data?.name}</span>
      <button type="button" onClick={handleLogout} disabled={logout.isPending}>
        Sair
      </button>
    </div>
  );
}
