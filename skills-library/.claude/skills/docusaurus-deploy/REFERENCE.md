# Docusaurus Deployment - Reference Documentation

## Architecture Overview

Deploys Docusaurus documentation sites to Kubernetes with automatic builds and versioning.
````
┌─────────────────────────────────────────────┐
│  Docusaurus Deployment Pipeline             │
│  ┌──────────────────────────────────────┐  │
│  │  1. Initialize Docusaurus project    │  │
│  │  2. Configure sidebars & navigation  │  │
│  │  3. Build static site (npm run build)│  │
│  │  4. Create nginx Docker image        │  │
│  │  5. Deploy to Kubernetes             │  │
│  │  6. Configure ingress                │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Nginx Pod (Serving /docs)           │  │
│  │  ├─ Static HTML/CSS/JS               │  │
│  │  ├─ Search index                     │  │
│  │  └─ Versioned docs                   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
````

## Features

### Documentation Structure
````
docs-site/
├── docs/                        # Documentation pages
│   ├── intro.md                # Getting Started
│   ├── architecture/
│   │   ├── overview.md
│   │   └── agents.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   └── deployment.md
│   └── api/
│       ├── triage-agent.md
│       └── concepts-agent.md
├── blog/                        # Optional blog
├── src/
│   └── pages/                   # Custom React pages
│       └── index.tsx            # Landing page
├── static/                      # Images, downloads
├── docusaurus.config.js        # Site configuration
├── sidebars.js                 # Navigation structure
└── package.json
````

### Pre-configured Features
- Search (Algolia DocSearch)
- Dark/light mode toggle
- Mobile-responsive design
- Code syntax highlighting
- Versioning support
- Blog functionality
- Custom React components

## Script Reference

### deploy.sh
````bash
./scripts/deploy.sh [dev|prod] [docs-dir]
````

**Steps Performed:**
1. Validate Docusaurus project structure
2. Install dependencies (`npm ci`)
3. Build static site (`npm run build`)
4. Create nginx Dockerfile
5. Build Docker image
6. Deploy to Kubernetes
7. Configure ingress
8. Display documentation URL

**Environment Profiles:**

**Development:**
- Base URL: `/docs`
- Host: `learnflow.local/docs`
- Build mode: Development
- Search: Disabled

**Production:**
- Base URL: `/docs`
- Host: Custom domain
- Build mode: Production
- Search: Algolia enabled
- CDN: Enabled

## Docusaurus Configuration

### docusaurus.config.js
````javascript
module.exports = {
  title: 'LearnFlow Documentation',
  tagline: 'AI-Powered Programming Learning Platform',
  url: 'https://docs.learnflow.com',
  baseUrl: '/docs/',
  
  themeConfig: {
    navbar: {
      title: 'LearnFlow',
      logo: {
        alt: 'LearnFlow Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left'
        },
        {
          href: 'https://github.com/learnflow',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'Architecture',
              to: '/docs/architecture/overview',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/learnflow',
            },
          ],
        },
      ],
    },
    
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
      additionalLanguages: ['python', 'javascript', 'bash', 'yaml'],
    },
  },
  
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/learnflow/docs/edit/main/',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
````

### sidebars.js
````javascript
module.exports = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/overview',
        'architecture/agents',
        'architecture/events',
        'architecture/state',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/quickstart',
        'guides/deployment',
        'guides/development',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/triage-agent',
        'api/concepts-agent',
        'api/debug-agent',
        'api/exercise-agent',
        'api/progress-agent',
      ],
    },
  ],
};
````

## Advanced Features

### Versioning
````bash
# Create new version
npm run docusaurus docs:version 1.0.0

# Structure after versioning
docs-site/
├── docs/              # Next version (unreleased)
├── versioned_docs/
│   └── version-1.0.0/ # Released version
└── versions.json      # Version list
````

### Search Integration (Algolia)
````javascript
// docusaurus.config.js
themeConfig: {
  algolia: {
    apiKey: 'your-api-key',
    indexName: 'learnflow',
    appId: 'your-app-id',
  },
}
````

### Custom Pages
````tsx
// src/pages/demo.tsx
import React from 'react';
import Layout from '@theme/Layout';

export default function Demo() {
  return (
    <Layout title="Live Demo">
      <div className="container">
        <h1>Try LearnFlow</h1>
        <iframe src="https://demo.learnflow.com" />
      </div>
    </Layout>
  );
}
````

### MDX Components
````mdx
---
title: Agent Architecture
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent Communication

<Tabs>
  <TabItem value="python" label="Python">
```python
    from dapr.clients import DaprClient
    
    with DaprClient() as client:
        client.publish_event(...)
```
  </TabItem>
  <TabItem value="curl" label="cURL">
```bash
    curl -X POST http://localhost:3500/v1.0/publish/...
```
  </TabItem>
</Tabs>
````

## Deployment

### Docker Integration
````dockerfile
# Dockerfile (auto-generated by script)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
````

### Nginx Configuration
````nginx
# nginx.conf
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
````

### Kubernetes Manifest
````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docs-deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: docs
        image: learnflow-docs:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: docs-service
spec:
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: docs-ingress
spec:
  rules:
  - host: learnflow.local
    http:
      paths:
      - path: /docs
        pathType: Prefix
        backend:
          service:
            name: docs-service
            port:
              number: 80
````

## Troubleshooting

### Build Failures
**Symptom:** `npm run build` fails

**Diagnosis:**
````bash
npm run build -- --debug
````

**Common Issues:**
1. Broken links → Check for invalid markdown links
2. Missing images → Verify paths in `/static`
3. Syntax errors → Validate MDX components

### Slow Build Times
**Symptom:** Build takes >5 minutes

**Optimization:**
````javascript
// docusaurus.config.js
module.exports = {
  future: {
    experimental_faster: true,
  },
};
````

### 404 Errors in Production
**Symptom:** Pages work locally but 404 in production

**Solution:**
Verify `baseUrl` matches deployment path:
````javascript
// docusaurus.config.js
module.exports = {
  baseUrl: '/docs/', // Must match ingress path
};
````

## CI/CD Integration

### GitHub Actions
````yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Docs
        run: |
          cd docs-site
          ./scripts/deploy.sh prod
````

## References

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [MDX Documentation](https://mdxjs.com/)
- [Algolia DocSearch](https://docsearch.algolia.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
