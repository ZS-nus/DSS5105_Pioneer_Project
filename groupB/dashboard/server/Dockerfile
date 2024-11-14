# Use Node.js LTS version
FROM node:20-slim

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install ALL dependencies including devDependencies
RUN npm install

# Copy source code
COPY . .

# Create a directory for keys if it doesn't exist
RUN mkdir -p keys

# Expose the port your app runs on
EXPOSE 5105

# Command to run the application with npm start
CMD ["npm", "start"]