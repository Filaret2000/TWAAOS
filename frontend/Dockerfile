# Imagine cu Node.js
FROM node:18

WORKDIR /app
# Copiază fișierele de configurare
COPY package.json package-lock.json ./
# Instalează dependențele
RUN npm install
# Copiază codul Vue.js
COPY . .
# Pornește serverul Vue.js
CMD ["npm", "run", "dev"]
