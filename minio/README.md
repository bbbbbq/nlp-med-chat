# MinIO Service

This directory contains the Docker Compose configuration for running a MinIO object storage service.

## How to Use

1.  **Start the service:**
    ```bash
    docker-compose up -d
    ```

2.  **Access the MinIO Console:**
    Open your web browser and navigate to [http://localhost:9001](http://localhost:9001).

3.  **Login Credentials:**
    -   **Username:** `minioadmin`
    -   **Password:** `minioadmin`

4.  **API Endpoint:**
    The S3-compatible API is available at `http://localhost:9000`.

5.  **Stop the service:**
    ```bash
    docker-compose down
    ```
