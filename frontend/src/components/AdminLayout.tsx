import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { ArrowLeft, Database, KeyRound, Layers, Play, Youtube } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { getAdminToken, setAdminToken } from "@/lib/api";

const NAV = [
  { to: "/admin/industries", label: "Industries", icon: Layers },
  { to: "/admin/keywords", label: "Keywords", icon: KeyRound },
  { to: "/admin/sources", label: "Sources", icon: Database },
  { to: "/admin/channels", label: "YouTube 채널", icon: Youtube },
  { to: "/admin/runs", label: "Runs", icon: Play },
];

export function AdminLayout() {
  const [token, setToken] = useState(getAdminToken());

  function saveToken() {
    setAdminToken(token);
    window.location.reload();
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-60 flex-shrink-0 border-r bg-muted/30 p-4">
        <Link to="/" className="mb-6 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> 대시보드로
        </Link>
        <h2 className="mb-4 text-lg font-bold">Admin</h2>
        <nav className="space-y-1">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                  isActive ? "bg-primary text-primary-foreground" : "hover:bg-accent",
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-8 space-y-2 rounded-md border bg-background p-3">
          <Label htmlFor="token" className="text-xs">
            Admin Token
          </Label>
          <Input
            id="token"
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder=".env의 ADMIN_API_TOKEN"
          />
          <Button size="sm" className="w-full" onClick={saveToken}>
            저장
          </Button>
        </div>
      </aside>
      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}
