#!/bin/bash
set -e

# Créer le répertoire pour le stockage persistant si nécessaire
mkdir -p "$HOME/data"
if [ -w "$HOME/data" ]; then
    echo "Persistent storage directory $HOME/data is writable"
else
    echo "Warning: $HOME/data is not writable, screenshots may not save correctly"
fi

# Configurer le mot de passe VNC
mkdir -p "$HOME/.vnc"
if [ -z "$VNC_PASSWORD" ]; then
    echo "Error: VNC_PASSWORD is not set"
    exit 1
fi
echo "${VNC_PASSWORD}" | vncpasswd -f > "$HOME/.vnc/passwd"
chmod 600 "$HOME/.vnc/passwd"

# Créer .Xauthority pour supprimer l'avertissement
touch "$HOME/.Xauthority"
chown ${USER}:${USER} "$HOME/.Xauthority"

# Démarrage du serveur VNC
echo "--- Démarrage du serveur VNC ---"
vncserver :1 -geometry ${VNC_RESOLUTION} -depth 24 || { echo "VNC server failed to start"; exit 1; }

# Attente pour l'initialisation
sleep 2

# Démarrage du proxy noVNC
echo "--- Démarrage du proxy noVNC ---"
websockify --web /usr/share/novnc/ ${NOVNC_PORT} localhost:${VNC_PORT} --verbose &

# Démarrage du serveur FastAPI
echo "--- Démarrage du serveur FastAPI ---"
uv run uvicorn mcp-web:app --host 0.0.0.0 --port 8001 > /home/mcp/fastapi.log 2>&1 &

# Attendre que le serveur FastAPI soit prêt
echo "Waiting for FastAPI server to start..."
timeout 10 bash -c "until nc -z localhost 8001; do sleep 1; done" || echo "Warning: FastAPI server did not start within 10 seconds, check /home/mcp/fastapi.log"

# Garder le conteneur en vie avec un processus foreground
exec tail -f /dev/null
