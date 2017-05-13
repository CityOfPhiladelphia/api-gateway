FROM node:boron

RUN mkdir -p /usr/src/config
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY package.json /usr/src/app/
RUN npm install

# COPY ../config/ /usr/src/config
COPY . /usr/src/app

EXPOSE 8080

CMD [ "npm", "start" ]
