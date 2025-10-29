FROM node:20-alpine

WORKDIR /app

# Dependencies separat für Cache
COPY package.json package-lock.json* ./
RUN npm install

# Source
COPY . .

# Vite Dev-Server nach außen exponieren
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "--port", "5173"]