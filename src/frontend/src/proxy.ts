import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const AUTH_PATHS = ["/login", "/register"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth_token")?.value;
  const role = request.cookies.get("user_role")?.value;

  const isAuthPath = AUTH_PATHS.includes(pathname);
  const isAdminPath = pathname.startsWith("/admin");

  // Already logged in → redirect auth pages to the correct dashboard
  if (isAuthPath && token) {
    const dest = role === "admin" ? "/admin/dashboard" : "/";
    return NextResponse.redirect(new URL(dest, request.url));
  }

  // Not logged in → redirect to login
  if (!isAuthPath && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Non-admin trying to access admin pages → redirect to customer home
  if (isAdminPath && role !== "admin") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
