# Building containers locally

By default, Mantis Docker setup pulls Mantis container from Github Container Registry. To test the changes you made locally, you need to build the mantis docker container locally. 

To achieve this, in your `setup/docker/docker-compose.yml` uncomment the following lines and comment the "image" directive.

```yaml
#build:
#  dockerfile: Dockerfile
#  context: ../../
```

Final mantis container block would look like, 

```yaml
mantis:
  build:
    dockerfile: Dockerfile
    context: ../../
#image: ghcr.io/phonepe/mantis:latest
... snipped ...
```

Now your mantis container is built locally and you can test your changes.