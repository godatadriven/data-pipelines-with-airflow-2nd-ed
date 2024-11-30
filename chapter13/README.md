

Run Instructions

# Run Instructions

0) Get into the project directory
    `cd chapter13_genai`


1) Run the Docker compose file
    `docker-compose up`

2) Once MinIO is running, you can access the MinIO web interface at `http://localhost:8083` with the following credentials:
    - Access Key: `airflow`
    - Pass: `apacheairflow`

3) Copy all the contents of the `.env.template` file in the root of the chapter folder to the `.env` file

4) Create an access key in MinIO UI and update the `.env` file in this repo on the following variables
    ```
    * MINIO_ID
    * MINIO_KEY
    ```
    Set the ide and key in the following variables of the .env file
    ```
    AWS_ACCESS_KEY_ID=MINIO_ID
    AWS_SECRET_ACCESS_KEY=MINIO_KEY
    ```
5) Add the OpenAI API keys to the `.env` file.

    a) For OpenAI API, you need to create an account and get the API key from the OpenAI website. 
        ```
        OPENAI_API_KEY=45dw2354910a454gf2ba90f3f238EXAMPLE
        ```

    b) For Azure OpenAI, you need to create text embedding resource in Azure and get the API key and endpoint from the Azure portal  and add the following variables to the `.env` file

        ```
        OPENAI_API_KEY=45dw2354910a454gf2ba90f3f238EXAMPLE
        AZURE_OPENAI_RESOURCE_NAME=project-openai-nl
        AZURE_OPENAI_ENDPOINT=https://project-openai-nl.openai.azure.com/
        ```
6) Stop docker-compose (ctrl+c) and run it again to apply the changes
    `docker-compose up --build`

7) Run the DAG in Airflow



Todo:
[] Test OpenAI api mode works 
[] add json parsing to the recipe in the app
[] Pass port 8084 to the chat as env var
[] Pass connection mode as a env var



