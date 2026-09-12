# Static site — no build step, just serve the files as-is with Caddy.
FROM caddy:alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html /usr/share/caddy/index.html
COPY assets/ /usr/share/caddy/assets/
