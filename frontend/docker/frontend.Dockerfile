FROM node:20-alpine

# Install tzdata for timezone support
RUN apk add --no-cache tzdata

WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
