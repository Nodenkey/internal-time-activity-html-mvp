FROM nginx:alpine

COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/styles.css /usr/share/nginx/html/frontend/styles.css
COPY frontend/app.js /usr/share/nginx/html/frontend/app.js

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
