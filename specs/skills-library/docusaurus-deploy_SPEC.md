# docusaurus-deploy Skill Specification

**Version:** 1.0.0  
**Status:** Draft  
**Owner:** Asadullah (asadullah48)  
**Created:** 2026-01-12  
**Hackathon:** Panaversity Hackathon III - Documentation Platform

---

## 1. Overview

### 1.1 Purpose
Deploy Docusaurus documentation sites to Kubernetes with static site optimization, CI/CD integration, and versioning support for LearnFlow documentation.

### 1.2 Scope
**In Scope:**
- Docusaurus production build and optimization
- Static file serving via Nginx
- Kubernetes deployment with ingress
- Multi-version documentation support
- Automated deployment script
- CI/CD pipeline integration

**Out of Scope:**
- Documentation content (user provides)
- Search indexing (can be added separately)
- Authentication (docs are public)

### 1.3 Token Budget
- **SKILL.md:** ≤120 tokens
- **Scripts:** 0 tokens (external files)
- **Results:** ≤30 tokens (deployment status)
- **Total:** ≤150 tokens per invocation

### 1.4 Success Metrics
- **Autonomy:** 95% (fully automated)
- **Efficiency:** 96% (static build + nginx)
- **Cross-agent compatibility:** 100% (standard patterns)

---

## 2. User Stories

### US1: Deploy Documentation Site
**As a** hackathon participant  
**I want** to deploy Docusaurus documentation to Kubernetes  
**So that** users can access comprehensive LearnFlow documentation

**Acceptance Criteria:**
- Production build optimized for static serving
- Nginx container ≤20MB (alpine-based)
- Kubernetes deployment with 1 replica
- Ingress configured for docs.learnflow.local

### US2: Support Multiple Versions
**As a** documentation maintainer  
**I want** version dropdown in documentation  
**So that** users can view docs for different releases

**Acceptance Criteria:**
- Docusaurus versioning configured
- All versions built and served
- Version switcher functional

---

## 3. Functional Requirements

### FR1: Multi-Stage Dockerfile
**Description:** Build Docusaurus and serve via Nginx

**Template:**
````dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
````

**Outputs:**
- Optimized image ≤20MB
- Static files pre-built
- Fast serving via Nginx

### FR2: Nginx Configuration
**Description:** Optimize Nginx for static site serving

**Template:**
````nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
````

### FR3: Kubernetes Deployment
**Description:** Deploy with minimal resources

**Template:**
````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-docs
spec:
  replicas: 1
  selector:
    matchLabels:
      app: learnflow-docs
  template:
    metadata:
      labels:
        app: learnflow-docs
    spec:
      containers:
      - name: docs
        image: learnflow-docs:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
          limits:
            memory: "64Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
````

### FR4: Service & Ingress
**Description:** Expose documentation externally

**Service:**
````yaml
apiVersion: v1
kind: Service
metadata:
  name: learnflow-docs
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: learnflow-docs
````

**Ingress:**
````yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: learnflow-docs-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: docs.learnflow.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: learnflow-docs
            port:
              number: 80
````

### FR5: Deployment Script
**Description:** Automate build and deployment

**Script:**
````bash
#!/bin/bash
set -e

NAMESPACE="${NAMESPACE:-default}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "📚 Deploying LearnFlow Documentation to Kubernetes"

# Build Docker image
docker build -t learnflow-docs:$IMAGE_TAG .

# Load to Minikube
if command -v minikube &> /dev/null; then
    minikube image load learnflow-docs:$IMAGE_TAG
fi

# Apply manifests
kubectl apply -f k8s/ -n $NAMESPACE

# Wait for deployment
kubectl rollout status deployment/learnflow-docs -n $NAMESPACE --timeout=3m

echo "✅ Documentation deployed!"
if command -v minikube &> /dev/null; then
    echo "🌐 Access at: $(minikube service learnflow-docs --url -n $NAMESPACE)"
fi
````

---

## 4. Docusaurus Configuration

### 4.1 Production Config
**docusaurus.config.js:**
````javascript
module.exports = {
  title: 'LearnFlow Documentation',
  tagline: 'AI-Powered Programming Learning Platform',
  url: 'https://docs.learnflow.local',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/your-org/learnflow/edit/main/docs/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  
  themeConfig: {
    navbar: {
      title: 'LearnFlow',
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'docsVersionDropdown',
          position: 'right',
        },
      ],
    },
    footer: {
      copyright: `Built with Docusaurus.`,
    },
  },
};
````

---

## 5. Testing Plan

### 5.1 Build Tests
- Docusaurus build completes successfully
- Docker image ≤20MB
- All pages accessible

### 5.2 Deployment Tests
- Pod reaches Running state
- Health endpoint returns 200
- Static assets load correctly
- Navigation works properly

---

## 6. SKILL.md Content
````markdown
# docusaurus-deploy

Deploy Docusaurus documentation sites to Kubernetes.

## Usage
```bash
# Deploy documentation
bash scripts/deploy.sh

# Custom image tag
IMAGE_TAG=v1.0.0 bash scripts/deploy.sh

# Custom namespace
NAMESPACE=production bash scripts/deploy.sh
```

## Features

- **Lightweight**: Nginx-based serving (≤20MB image)
- **Fast**: Static site with optimized caching
- **Versioned**: Multi-version documentation support
- **Production-ready**: Gzip, cache headers, health checks

## Configuration

Place templates in your Docusaurus project:
```bash
cp Dockerfile /path/to/docusaurus/
cp nginx.conf /path/to/docusaurus/
cp -r k8s/ /path/to/docusaurus/
```

## Token Usage

- SKILL.md: ~115 tokens
- Scripts: External (0 tokens)
- Results: ~28 tokens
````

---

## 7. Acceptance Criteria

**Skill complete when:**
- ✅ Dockerfile builds image ≤20MB
- ✅ Deployment succeeds in Minikube
- ✅ Documentation accessible via ingress
- ✅ Health endpoint returns 200
- ✅ Token budget ≤150 tokens

---

**End of Specification**
