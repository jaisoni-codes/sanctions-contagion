FROM node:20-slim
WORKDIR /app
COPY web/package.json .
RUN npm install
COPY web/ .
CMD ["npm", "run", "dev"]
