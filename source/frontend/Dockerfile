FROM node:20-alpine

WORKDIR /app

# Copia package files
COPY package*.json ./

# Installa dipendenze
RUN npm ci

# Copia tutto il codice
COPY . .

# Espone la porta Vite
EXPOSE 5173

# Avvia il dev server
CMD ["npm", "run", "dev"]

