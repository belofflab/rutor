uvicorn src.application:app --port 8080

docker build -t rutor .
docker run -d --name rutor -p 8080:8080 rutor