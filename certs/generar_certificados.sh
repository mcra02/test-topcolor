#!/bin/bash

# Configuración
SUBDOMAIN="topcolor"
DOMAIN="cebralab.com"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"
EMAIL="admin@${DOMAIN}"

# Detener cualquier servicio que use el puerto 80
echo "Deteniendo servicios en puerto 80..."
sudo fuser -k 80/tcp

# Instalar certbot si no está instalado
if ! command -v certbot &> /dev/null; then
    echo "Instalando certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

# Generar certificados en modo standalone
echo "Generando certificados para ${FULL_DOMAIN}..."
sudo certbot certonly --standalone \
    -d "${FULL_DOMAIN}" \
    --config-dir ./certs \
    --work-dir ./certs \
    --logs-dir ./certs \
    --agree-tos \
    --email "${EMAIL}" \
    --non-interactive

# Ajustar permisos
echo "Ajustando permisos..."
sudo chown -R $USER:$USER ./certs
chmod 600 "./certs/live/${FULL_DOMAIN}/*.pem"

echo "Certificados generados en:"
echo "- ./certs/live/${FULL_DOMAIN}/fullchain.pem"
echo "- ./certs/live/${FULL_DOMAIN}/privkey.pem" 