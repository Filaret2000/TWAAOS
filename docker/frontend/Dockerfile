FROM node:16-alpine

WORKDIR /app

# Instalare dependențe
COPY frontend/package*.json ./
RUN npm install

# Copierea fișierelor de configurare
COPY frontend/.eslintrc.js ./
COPY frontend/babel.config.js ./
COPY frontend/vue.config.js ./

# Copierea codului sursă
COPY frontend/ .

# Expunere port
EXPOSE 8080

# Comandă de pornire pentru dezvoltare
CMD ["npm", "run", "serve"]

# Pentru build de producție, decomentați următoarele linii și comentați comanda de mai sus
# RUN npm run build
# FROM nginx:alpine
# COPY --from=0 /app/dist /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
