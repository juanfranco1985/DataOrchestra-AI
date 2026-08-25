import { fileURLToPath } from 'node:url';

/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_PAGES === "true";
const repositoryBasePath = process.env.NEXT_PUBLIC_BASE_PATH || "/DataOrchestra-AI";

const webRoot = fileURLToPath(new URL('.', import.meta.url));

const nextConfig = {
  reactStrictMode: true,
  turbopack: {
    root: webRoot,
  },
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  basePath: isGithubPages ? repositoryBasePath : "",
  assetPrefix: isGithubPages ? `${repositoryBasePath}/` : "",
  env: {
    NEXT_PUBLIC_BASE_PATH: isGithubPages ? repositoryBasePath : ""
  }
};

export default nextConfig;
