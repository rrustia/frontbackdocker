FROM nginx:1.27-alpine

# I use this Nginx config to proxy API requests to the backend service.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# I copy static frontend assets.
COPY index.html /usr/share/nginx/html/index.html
COPY app.js /usr/share/nginx/html/app.js
COPY styles.css /usr/share/nginx/html/styles.css
