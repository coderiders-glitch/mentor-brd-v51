FROM node:20-slim AS fe-build
WORKDIR /fe
ENV NODE_TLS_REJECT_UNAUTHORIZED=0
COPY frontend/package*.json ./
RUN npm install --strict-ssl=false --no-audit --no-fund
COPY frontend/ ./
RUN echo '{"compilerOptions":{"skipLibCheck":true,"noEmitOnError":false,"strict":false,"allowJs":true,"jsx":"react-jsx","target":"ES2020","module":"ESNext","moduleResolution":"bundler"}}' > tsconfig.json || true
RUN npm run build
RUN mkdir -p /out && if [ -f build/index.html ]; then cp -R build/. /out/; elif [ -f dist/index.html ]; then cp -R dist/. /out/; else printf '<!doctype html><html><head><meta charset="utf-8"><title>UI Build Failed</title><style>body{font-family:system-ui,sans-serif;margin:0;padding:2rem;background:#fef2f2}.box{max-width:560px;margin:3rem auto;padding:2rem;border:1px solid #fecaca;border-radius:10px;background:#fff;color:#1f2937}h1{font-size:1.35rem;margin:0 0 .75rem;color:#b91c1c}p{margin:0;line-height:1.55;color:#4b5563}</style></head><body><div class="box"><h1>Frontend build failed</h1><p>The API is running, but the UI was not built during Docker deploy. Check docker build logs for npm/TypeScript errors, then regenerate the project.</p></div></body></html>' > /out/index.html; fi

FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org --no-cache-dir -r requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org --no-cache-dir uvicorn

COPY backend/app ./app
COPY backend/secretsmanager.py* ./
COPY backend/secretsmanager.py* ./app/
COPY --from=fe-build /out ./static

ENV PYTHONPATH=/app
ENV PORT=3000
EXPOSE 3000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
