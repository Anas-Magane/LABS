import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const subrequest = request.headers.get("x-middleware-subrequest");
  if (subrequest === "middleware") {
    return NextResponse.next();
  }
  return new NextResponse("Forbidden", { status: 403 });
}

export const config = {
  matcher: ["/flag"],
};
