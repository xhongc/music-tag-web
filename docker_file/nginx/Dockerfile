FROM nginx

EXPOSE 80
RUN mkdir -p /home/ubuntu/django_vue_log
RUN rm /etc/nginx/conf.d/default.conf
ADD ./docker_file/nginx/nginx-dv.conf /etc/nginx/conf.d/
ADD ./templates/index.html /home/ubuntu/