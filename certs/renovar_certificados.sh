#!/bin/bash

# Configuración
SUBDOMAIN="topcolor"
DOMAIN="cebralab.com"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

# Renovar certificados usando la carpeta certs
echo "Renovando certificados para ${FULL_DOMAIN}..."
sudo certbot renew \
    --config-dir ./certs \
    --work-dir ./certs \
    --logs-dir ./certs \
    --quiet

# Ajustar permisos
echo "Ajustando permisos..."
sudo chown -R $USER:$USER ./certs
chmod 600 "./certs/live/${FULL_DOMAIN}/*.pem"

echo "Certificados renovados en:"
echo "- ./certs/live/${FULL_DOMAIN}/fullchain.pem"
echo "- ./certs/live/${FULL_DOMAIN}/privkey.pem"

# Reiniciar servicios que usan los certificados (si es necesario)
# systemctl restart nginx
# systemctl restart uvm-integration-api 