# DocsVision

## 🚀 How to Use

### 📌 Commands for bot


- create migration
```bash
alembic revision --autogenerate -m "{about}"
```

- download model
```bash
wget https://huggingface.co/meyiapir/DocsVision/resolve/main/full_model_epoch_10.pt?download=true
```

### 🐳 Running in Docker _(recommended method)_

-   configure environment variables in `.env` file

-   start services

    ```bash
    docker compose -f docker-compose.dev.yml up -d --build
    ```
