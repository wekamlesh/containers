# Base Image
FROM nginx:alpine

#copy the index.thml page to /usr/share/nginx/html/
COPY index.html /usr/share/nginx/html/

#Expose Nginx Port
EXPOSE 80

#Start NgnixService
CMD ["nginx", "-g", "daemon off;"]
