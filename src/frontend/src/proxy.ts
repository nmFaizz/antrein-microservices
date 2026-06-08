import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const AUTH_PATHS = ["/login", "/register"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth_token")?.value;

  const isAuthPath = AUTH_PATHS.includes(pathname);

  // Already logged in → skip auth pages
  if (isAuthPath && token) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Not logged in → redirect to login (except auth pages themselves)
  if (!isAuthPath && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
