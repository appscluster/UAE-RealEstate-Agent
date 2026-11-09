FROM node:20-slim AS build
WORKDIR /app
COPY frontend/package.json /app/package.json
COPY frontend/vite.config.ts /app/vite.config.ts
COPY frontend/index.html /app/index.html
COPY frontend/src /app/src
RUN npm install --no-audit --no-fund && npm run build

FROM node:20-slim
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist /app/dist
EXPOSE 43231
CMD ["serve", "-s", "dist", "-l", "43231"]
