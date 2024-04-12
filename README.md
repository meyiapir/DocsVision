# DocsVision

## 🚀 How to Use

### 📌 Commands for bot


- create migration
```bash
alembic revision --autogenerate -m "{about}"
```


### 🐳 Running in Docker _(recommended method)_

-   configure environment variables in `.env` file

-   start services

    ```bash
    docker compose -f docker-compose.dev.yml up -d --build
    ```

-   make migrations

    ```bash
    docker compose exec bot alembic upgrade head
    ```
