# image-processing-function-app

This is a simple function app that processes images uploaded to an Azure Blob Storage container. The function app is written in Python and uses the Azure Functions Python runtime.

## Testing the function app locally
Build the Docker image using the following command:
```bash
docker build -t image-processing-function-app:dev .
```

Run the Docker container using the following command:
```bash
docker run -p 80:80 \
-e AZURE_STORAGE_CONNECTION_STRING="some_connection_string" \
-e AZURE_STORAGE_CONTAINER_NAME="some_container_name" \
-e AZURE_TABLE_CONNECTION_STRING="some_connection_string" \
-e AZURE_TABLE_NAME="some_table_name" \
-e AZURE_TABLE_PARTITION_KEY="PartitionKey" \
image-processing-function-app:dev
```

The function app will be available at `http://localhost/api/v1`.
You can test by uploading an image to the rest api endpoint.
```bash
curl -X POST "http://localhost/api/v1" \
 -H "Content-Type: multipart/form-data" \
 -F "file=@tests/resources/car.jpg" \
 -F "metadata=@tests/resources/metadata.json;type=application/json"
```
