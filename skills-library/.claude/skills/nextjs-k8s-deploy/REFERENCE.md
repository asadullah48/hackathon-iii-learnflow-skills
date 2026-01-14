# Next.js Kubernetes Deployment - Reference Documentation

## Architecture Overview

Deploys Next.js applications with SSR/SSG support, optimized Docker images, and Kubernetes ingress.
```
┌─────────────────────────────────────────┐
│  Next.js Deployment                     │
│  ┌───────────────────────────────────┐ │
│  │  Next.js Pod (Replicas: 2)        │ │
│  │  ├─ Node.js Server (Port 3000)    │ │
│  │  ├─ Static Assets (.next/static)  │ │
│  │  └─ API Routes (/api/*)           │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Service (ClusterIP)              │ │
│  │  Port: 80 → 3000                  │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Ingress                          │ │
│  │  Host: learnflow.local            │ │
│  │  Path: /*                         │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Features Included

### Application Structure
```
nextjs-app/
├── app/                      # App Router (Next.js 13+)
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   └── api/                 # API routes
├── components/              # React components
│   ├── CodeEditor.tsx       # Monaco editor
│   ├── ChatInterface.tsx    # AI chat UI
│   └── ProgressDashboard.tsx
├── lib/
│   ├── dapr-client.ts       # Dapr HTTP client
│   └── auth-config.ts       # Better Auth config
├── public/                  # Static files
├── next.config.js           # Next.js config
├── Dockerfile               # Multi-stage build
└── k8s/
    ├── deployment.yaml      # K8s deployment
    ├── service.yaml         # K8s service
    ├── ingress.yaml         # Ingress rules
    └── configmap.yaml       # Environment config
```

### Monaco Editor Integration
```typescript
// components/CodeEditor.tsx
import Editor from '@monaco-editor/react';

export function CodeEditor() {
  return (
    <Editor
      height="500px"
      defaultLanguage="python"
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
      }}
    />
  );
}
```

### Dapr Integration
```typescript
// lib/dapr-client.ts
const DAPR_HOST = process.env.DAPR_HOST || 'localhost';
const DAPR_PORT = process.env.DAPR_HTTP_PORT || '3500';

export async function invokeService(
  serviceId: string,
  method: string,
  data?: any
) {
  const url = `http://${DAPR_HOST}:${DAPR_PORT}/v1.0/invoke/${serviceId}/method/${method}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function publishEvent(topic: string, data: any) {
  const url = `http://${DAPR_HOST}:${DAPR_PORT}/v1.0/publish/pubsub/${topic}`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}
```

## Script Parameters

### deploy.sh
```bash
./scripts/deploy.sh [dev|prod] [app-name]
```

**Steps Performed:**
1. Build optimized Docker image
2. Push to registry (or load to Minikube)
3. Apply ConfigMap with environment variables
4. Deploy application with replicas
5. Create service and ingress
6. Wait for rollout completion
7. Display access URL

**Environment Profiles:**

**Development:**
- Image: Local build
- Replicas: 1
- Resources: Minimal
- Ingress: `learnflow.local`

**Production:**
- Image: Registry (DockerHub/ECR)
- Replicas: 3
- Resources: Production-grade
- Ingress: Custom domain
- Health checks: Enabled
- Autoscaling: HPA configured

## Dockerfile Optimization

### Multi-Stage Build
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["npm", "start"]
```

**Size Comparison:**
- Full build: ~1.2GB
- Multi-stage: ~180MB
- With alpine + pruning: ~120MB

### Build Caching
```bash
# Use BuildKit for layer caching
DOCKER_BUILDKIT=1 docker build --cache-from=myapp:latest -t myapp:new .
```

## Advanced Configuration

### Environment Variables
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nextjs-config
data:
  NEXT_PUBLIC_API_URL: "http://api.learnflow.local"
  DAPR_HOST: "localhost"
  DAPR_HTTP_PORT: "3500"
  OPENAI_API_KEY: "" # Use secret instead
```

### Secret Management
```bash
kubectl create secret generic nextjs-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=auth-secret=$AUTH_SECRET \
  -n learnflow
```

### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nextjs-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - learnflow.com
    secretName: learnflow-tls
  rules:
  - host: learnflow.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nextjs-service
            port:
              number: 80
```

## Troubleshooting

### Build Failures
**Symptom:** `npm run build` fails

**Common Causes:**
1. TypeScript errors
2. Missing environment variables
3. Import path issues

**Solution:**
```bash
# Check build locally
npm run build

# Validate TypeScript
npx tsc --noEmit

# Check environment
npm run build -- --debug
```

### Pod CrashLoopBackOff
**Symptom:** Pod restarts repeatedly

**Diagnosis:**
```bash
kubectl logs {pod-name} --previous
kubectl describe pod {pod-name}
```

**Common Causes:**
1. Port conflict (3000 already in use)
2. Missing dependencies
3. Build artifacts not copied

**Solution:**
```bash
# Verify Dockerfile COPY commands
# Ensure .next directory is copied
# Check exposed port matches container
```

### Slow Page Loads
**Symptom:** Initial page load >3 seconds

**Diagnosis:**
```bash
# Check bundle size
npm run build -- --profile

# Analyze bundles
npx @next/bundle-analyzer
```

**Optimization:**
```javascript
// next.config.js
module.exports = {
  compress: true,
  swcMinify: true,
  images: {
    domains: ['cdn.example.com'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
  },
};
```

## Performance Optimization

### Static Generation
```typescript
// app/docs/[slug]/page.tsx
export async function generateStaticParams() {
  // Pre-render these pages at build time
  return [
    { slug: 'getting-started' },
    { slug: 'api-reference' },
  ];
}
```

### Image Optimization
```typescript
import Image from 'next/image';

<Image
  src="/hero.png"
  alt="LearnFlow"
  width={800}
  height={600}
  priority
/>
```

### Code Splitting
```typescript
import dynamic from 'next/dynamic';

const CodeEditor = dynamic(() => import('@/components/CodeEditor'), {
  ssr: false,
  loading: () => <p>Loading editor...</p>,
});
```

### Edge Runtime
```typescript
// app/api/check/route.ts
export const runtime = 'edge';

export async function GET() {
  return Response.json({ status: 'ok' });
}
```

## Monitoring

### Health Checks
```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
}
```

### Custom Metrics
```typescript
// lib/metrics.ts
export function trackPageView(page: string) {
  if (typeof window !== 'undefined') {
    window.gtag?.('event', 'page_view', { page });
  }
}
```

## Autoscaling

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nextjs-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nextjs-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Security

### Content Security Policy
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval';",
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
];

module.exports = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
};
```

### CORS Configuration
```typescript
// middleware.ts
import { NextResponse } from 'next/server';

export function middleware(request: Request) {
  const response = NextResponse.next();
  response.headers.set('Access-Control-Allow-Origin', '*');
  return response;
}
```

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [Monaco Editor React](https://github.com/suren-atoyan/monaco-react)
- [Dapr JavaScript SDK](https://docs.dapr.io/developing-applications/sdks/js/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
