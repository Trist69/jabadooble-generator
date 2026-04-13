FROM node:20-slim

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 5173
CMD ["sh", "-c", "npx svelte-kit sync && npm run dev -- --host 0.0.0.0"]
