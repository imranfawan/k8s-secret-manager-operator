# k8s-secret-manager-operator

A docker image is used by the K8s secret manager controller helm chart.

## Building and tagging the tools image

A github action builds the tools image and pushes it to [DockerHub](https://hub.docker.com/r/imranfawan/tools) whenever a new release is defined in github.

The image is tagged with the release number.
