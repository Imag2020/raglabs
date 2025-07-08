# Utiliser l'image de base Ubuntu 22.04 LTS
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Définir les variables d'environnement avec des valeurs par défaut
ENV USER=mcp
ENV HOME=/home/${USER}
ENV VNC_PORT=5901
ENV NOVNC_PORT=6901
ENV VNC_RESOLUTION=1366x768

# Mettre à jour les paquets et installer les dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Outils système
    sudo \
    wget \
    curl \
    git \
    software-properties-common \
    # Environnement de bureau XFCE
    xfce4 \
    xfce4-goodies \
    xfce4-terminal \
    # VNC et noVNC
    tightvncserver \
    novnc \
    websockify \
    # Python
    python3 \
    python3-pip \
    # Polices et dépendances graphiques
    xfonts-base \
    xfonts-100dpi \
    xfonts-75dpi \
    xauth \
    dbus-x11 \
    # Commandes supplémentaires
    openssh-client \
    scrot \
    cups \
    cups-pdf \
    # Firefox pour Selenium et Playwright
    firefox \
    # Dépendances supplémentaires pour Python
    python3-tk \
    python3-dev \
    xclip \
    xsel \
    # Nettoyage
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installation de Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installer les librairies Python
RUN pip3 install --no-cache-dir \
    uv \
    fastapi \
    uvicorn \
    pydantic \
    selenium \
    playwright \
    pyautogui \
    bs4 \
    keyboard \
    pillow \
    pyperclip \
    opencv-python \
    psutil \
    pdfkit \
    && python3 -m playwright install --with-deps firefox

# Créer l'utilisateur 'mcp' et configurer les permissions
RUN useradd -m -s /bin/bash ${USER} && \
    adduser ${USER} sudo && \
    adduser ${USER} lpadmin && \
    echo "${USER} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Configurer VNC sans mot de passe (sera fait au démarrage via start.sh)
RUN mkdir -p ${HOME}/.vnc && \
    echo "#!/bin/bash\n\
xrdb \$HOME/.Xresources\n\
startxfce4 &" > ${HOME}/.vnc/xstartup && \
    chmod +x ${HOME}/.vnc/xstartup && \
    chown -R ${USER}:${USER} ${HOME}

# Créer un répertoire pour le bureau et ajouter des lanceurs
RUN mkdir -p ${HOME}/Desktop && \
    echo "[Desktop Entry]\nVersion=1.0\nType=Application\nName=Terminal\nExec=xfce4-terminal\nIcon=utilities-terminal\nCategories=Application;System;" > ${HOME}/Desktop/terminal.desktop && \
    echo "[Desktop Entry]\nVersion=1.0\nName=Google Chrome\nExec=/usr/bin/google-chrome-stable %U --no-sandbox\nTerminal=false\nIcon=google-chrome\nType=Application" > ${HOME}/Desktop/google-chrome.desktop && \
    chmod +x ${HOME}/Desktop/*.desktop && \
    chown -R ${USER}:${USER} ${HOME}/Desktop

# Créer le répertoire pour le stockage persistant
RUN mkdir -p ${HOME}/data && chown -R ${USER}:${USER} ${HOME}/data

# Copier le script FastAPI
COPY mcp-web.py /home/mcp/mcp-web.py
RUN chown ${USER}:${USER} /home/mcp/mcp-web.py

# Copier et rendre exécutable le script de démarrage
COPY start.sh /start.sh
RUN chmod 755 /start.sh

# Exposer les ports
EXPOSE ${NOVNC_PORT}
EXPOSE ${VNC_PORT}
EXPOSE 8001

# Changer le contexte pour l'utilisateur non-root
USER ${USER}
WORKDIR ${HOME}

# Lancer le script via bash
ENTRYPOINT ["/bin/bash", "/start.sh"]
