FROM nginx:1.27-alpine

# This Nginx config proxies API requests to the backend service.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static frontend assets are copied into the image.
COPY index.html /usr/share/nginx/html/index.html
COPY app.js /usr/share/nginx/html/app.js
COPY styles.css /usr/share/nginx/html/styles.css
