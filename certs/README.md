# Certificados SSL

Esta carpeta contiene los certificados SSL para el dominio dev.mcra02.com.

## Generar certificados con Certbot

1. Instalar Certbot:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. Generar certificados (modo standalone):
```bash
sudo certbot certonly --standalone -d dev.mcra02.com
```

Los certificados se generarán en:
- `/etc/letsencrypt/live/dev.mcra02.com/fullchain.pem`
- `/etc/letsencrypt/live/dev.mcra02.com/privkey.pem`

3. Copiar los certificados a esta carpeta:
```bash
sudo cp /etc/letsencrypt/live/dev.mcra02.com/fullchain.pem certs/
sudo cp /etc/letsencrypt/live/dev.mcra02.com/privkey.pem certs/
```

4. Asegurar los permisos:
```bash
sudo chown -R $USER:$USER certs/
chmod 600 certs/*.pem
```

## Renovación automática

Los certificados de Let's Encrypt expiran cada 90 días. Para renovarlos automáticamente:

1. Crear un script de renovación:
```bash
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/dev.mcra02.com/fullchain.pem certs/
cp /etc/letsencrypt/live/dev.mcra02.com/privkey.pem certs/
```

2. Agregar al crontab:
```bash
0 0 1 * * /ruta/al/script/renovar_certificados.sh
``` 