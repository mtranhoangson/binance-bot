#########################
### build environment ###
#########################

# base image
FROM node:12 as builder

# install chrome for protractor tests
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
#RUN apt-get update && apt-get install -yq google-chrome-stable

# set working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY ./admin/package.json /usr/src/app/package.json
COPY ./admin/package-lock.json /usr/src/app/package-lock.json
RUN npm install --python=python3.7
#RUN npm config set python python3.7
#RUN npm i -g npm-check-updates --force
#RUN npm uninstall tailwindcss postcss autoprefixer
#RUN npm install -D tailwindcss@npm:@tailwindcss/postcss7-compat postcss@^7 autoprefixer@^9
#RUN npm install --force
RUN npm i --package-lock-only
RUN npm audit fix
RUN npm install -g @angular/cli


# add app
COPY ./admin /usr/src/app

# run tests
#RUN ng test --watch=false

# generate build
#RUN npm run lint && \ --depricated
#RUN npm run build-prod
#RUN ng build --prod --output-path app_docker
RUN ng build --prod --output-path release

##################
### production ###
##################
FROM python:3.7-slim
MAINTAINER Igor Iliunin <ilunin.igor@gmail.com>

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

ENV \
  TRADE_DIR=/usr/src/trades \
  TRADE_COMPLETED_DIR=/usr/src/complete_trades \
  CONF_DIR=/usr/src/configs
#  LOGS_DIR=/usr/src/logs

COPY requirements.txt /usr/src/app/

RUN \
  apt-get update && \
  apt-get install -y && \
  apt-get install -y tzdata && \
  pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

VOLUME ["/usr/src/trades", "/usr/src/configs"]

COPY . /usr/src/app
#COPY --from=builder /usr/src/app/dist/admin /usr/src/app/API/templates
COPY --from=builder /usr/src/app/release /usr/src/app/API/templates

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 3000
CMD ["python3", "main.py", "api"]
