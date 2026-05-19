const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export function siteHref(path: string): string {
  if (!path.startsWith("/")) {
    return path;
  }

  return `${basePath}${path}`;
}
