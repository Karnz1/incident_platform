FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY . .

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]