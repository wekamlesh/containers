# Use an official Portainer image from Docker Hub
FROM portainer/portainer-ce:latest

# Expose the port that Portainer will use
EXPOSE 9000

# Create a volume for persistent data
VOLUME ["/data"]

# Start Portainer
CMD ["--host", "unix:///var/run/docker.sock"]
