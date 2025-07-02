# Workshop RagLabs : Ingénierie IA

### Construire et orchestrer des agents, de Python pur aux plateformes open-source

### LLM VLM  /  MCP / n8n / RAG Agentic RAG /  No Code (Gemeini-Cli & Cline)

Bienvenue dans ce workshop RagLabs ! Ce workshop explore les solutions et approches état de l'art (SOTA) en ingénierie IA, couvrant le pipeline de l'accès simple aux grands modèles de langage (LLM) et de vision (VLM) à la création d'agents IA et d'applications web interactives boostées par l'IA. Vous apprendrez à construire des solutions from scratch et à implémenter des outils open-source tels que les serveurs MCP (Model Context Protocol), les outils No code tels que n8n, Gemini-CLI, et VS+Cline, avec une approche pratique et progressive.

## 🚀 Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- [Python 3.9+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/) (recommandé)
- Un environnement virtuel (ex: `venv` ou `conda`)

## 🛠️ Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/imag2020/raglabs.git
    cd raglabs
    ```

2.  **Créez et activez un environnement virtuel :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```

3.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurez vos clés d'API :**
    Créez un fichier `.env` à la racine du projet en copiant le modèle `.env.example` (que vous devez créer).
    ```
    GEMINI_OPENAI_API_KEY="sk-..."
    OPENAI_API_KEY="sk-..."
    HUGGINGFACE_TOKEN="hf_..."
    ```

5.  **Lancez Jupyter Lab :**
    ```bash
    jupyter lab
    ```
    Naviguez ensuite dans le dossier `notebooks/` pour commencer la formation.

---

## 📚 Plan de la Formation

Voici le détail des modules que nous allons parcourir. Chaque module correspond à un notebook Jupyter.

*   **[1.Introduction aux LLMs et VLMs (Local & API)](./notebooks/01_llm_vlm_access.ipynb)**
    *   Comprendre les bases de l'interaction avec les LLMs/VLMs et configurer un environnement pour interagir avec ces modèles.

*   **[2. Serveurs & Clients MCP](./notebooks/02_mcp_servers_clients.ipynb)**
    *  Apprendre à configurer et utiliser des serveurs MCP pour des interactions avancées avec les LLMs.

*   **[3. Créer un Agent IA "from scratch"](./notebooks/03_agent_ia_from_scratch.ipynb)**
    *   Comprendre les principes fondamentaux des agents IA et leur implémentation sans dépendances complexes.

*   **[4. Agents No-Code (Llama-Index, GEMINI-CLI)](./notebooks/04_agents_no_code.ipynb)**
    *   Découvrez comment utiliser des outils puissants en ligne de commande pour créer des agents et des applications sans écrire de code complexe.

*   **[5. n8n : Installation locale et workflows](./notebooks/05_n8n_introduction.ipynb)**
    *   Installez la plateforme d'automatisation n8n et créez vos premiers workflows d'automatisation.

*   **[6. Exemple de RAG Multi-Modal Avancé](./notebooks/06_rag_multimodal_rag.ipynb)**
    *    Comprendre et appliquer les concepts de RAG pour des cas d'usage avancés.

*   **[7. Construire une WebApp "NotebooLM"](./notebooks/07_webapp_notebooklm.ipynb)**
    *   Utiliser n8n & fastapi comme backend et construire un frontend React/Vite en No Code pour une WebApp RAG.

---

## 🤝 Contribution

N'hésitez pas à ouvrir une *issue* ou une *pull request* si vous trouvez des erreurs ou avez des suggestions d'amélioration !
