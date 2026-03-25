FROM node:16.14.0

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 8080

CMD ["npm", "run", "dev"]