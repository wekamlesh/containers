# Portainer with Podman

This repository contains a Podman configuration to build and run a Portainer container with persistent storage.


## Build the Image
` podman build -t my-portainer . `  

## Run the container with the volume and port mapping

```
podman run -d \
  -p 9000:9000 \
  -v portainer_data:/data \
  --name=portainer \
  portainer-standalone
```
