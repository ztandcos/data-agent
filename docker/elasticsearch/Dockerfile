FROM docker.elastic.co/elasticsearch/elasticsearch:8.19.10

USER root

RUN curl -fsSL \
    https://github.com/infinilabs/analysis-ik/releases/download/v8.19.10/elasticsearch-analysis-ik-8.19.10.zip \
    -o /tmp/elasticsearch-analysis-ik-8.19.10.zip \
    && /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch \
    file:///tmp/elasticsearch-analysis-ik-8.19.10.zip \
    && rm -f /tmp/elasticsearch-analysis-ik-8.19.10.zip

RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins

USER elasticsearch
