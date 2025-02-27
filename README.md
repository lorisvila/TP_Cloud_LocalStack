# TP_Cloud_Messagerie

## Description
Ce projet est une application utilisant Docker et LocalStack pour simuler des services AWS en local. Elle permet de s'expérimenter avec AWS-CLI et de prototyper des programmes informatiques utilisant des services AWS comme S3, DynamoDB et SQS.

## Architecture de l'Application
L'application fonctionne avec un conteneur utilisant `docker-compose` :

- **Conteneur**: localstack
- **Image**: `localstack/localstack:latest`
- **Rôle**: Héberger/simuler des services AWS (S3, DynamoDB, SQS)

## Création du Docker-Compose
L'application nécessite un seul conteneur :

- **Volume**: Non disponible (les données sont perdues à chaque redémarrage du conteneur)
- **Port Ouvert**: 4566 pour permettre aux clients de communiquer avec l'API de LocalStack
- **Variables d'Environnement**: Configuration de LocalStack pour mettre en place les services S3, DynamoDB et SQS

## Installation
Clonez le repository et démarrez le conteneur Docker :
```sh
git clone https://github.com/lorisvila/TP_Cloud_Messagerie/
cd TP_Cloud_Messagerie
docker-compose up
