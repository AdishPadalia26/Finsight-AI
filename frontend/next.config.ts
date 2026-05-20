import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',        // Static HTML export for S3 + CloudFront
  trailingSlash: true,     // S3 serves /about/ → about/index.html
  images: {
    unoptimized: true,     // S3 can't run Next.js image optimization server
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? '',
  },
}

export default nextConfig
