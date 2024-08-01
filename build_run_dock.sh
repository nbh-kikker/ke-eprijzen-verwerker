#!/bin/bash
git pull

# Get the latest git commit hash
tag_name=$(git rev-parse --short HEAD)
data_folder=$(pwd)/data
log_folder=$(pwd)/logging
docker_name="prijs-verwerker-${tag_name}"  # Modified to include the commit hash

PS3='Build for (Ocean Server/Raspberry Server)?: '
server_options=("Ocean Server" "Raspberry Server" "Pixi Server")
select server in "${server_options[@]}"
do
    case $server in
        "Ocean Server")
            dockerfile="Dockerfile"
            image_name="Ocean:3.12.0-slim-buster"
            break
            ;;
        "Raspberry Server")
            dockerfile="rasp.Dockerfile"
            image_name="Rasp:3.12-slim-bookworm"
            break
            ;;
        "Pixi Server")
            dockerfile="pixi.Dockerfile"
            image_name="Pixi:3.12-bookworm"
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

PS3='Build What?: '
options=("acc" "prod" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "acc")
            echo "your choice is ACC"
            break
            ;;
        "prod")
            echo "your choice is PROD"
            break
            ;;
        "Quit")
            exit 0
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

# Building and running the docker container
docker build -f "$dockerfile" -t "$docker_name" .
docker run -it -d --restart on-failure:3 --network="host" -v "$log_folder:/src/logging" -e "TZ=Europe/Amsterdam" --log-opt tag="$docker_name/$image_name" --name="$docker_name" "$docker_name"

docker ps -a
