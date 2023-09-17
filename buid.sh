docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)

docker build -f Dockerfile.app -t finances .

docker run -d -p 80:5001 finances