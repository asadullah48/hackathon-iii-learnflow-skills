// Implements section 4.1: Next.js Configuration from nextjs-k8s-deploy_SPEC.md

module.exports = {
  output: 'standalone', // For Docker deployment
  compress: true,       // Gzip compression
  poweredByHeader: false,
  images: {
    unoptimized: true,  // Or configure external CDN
  },
  env: {
    DAPR_HTTP_PORT: process.env.DAPR_HTTP_PORT || '3500',
  }
}
