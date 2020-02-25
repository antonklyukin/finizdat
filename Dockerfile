# Version 4

FROM python:3.7

RUN groupadd --gid 1000 antony \
    && useradd --uid 1000 --gid antony --shell /bin/bash --create-home antony

WORKDIR /home/antony

RUN apt-get update \
    && apt-get install -y --no-install-recommends libxml2 libxslt1.1 

RUN apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

ADD requirements.txt /home/antony/requirements.txt

RUN pip install -r /home/antony/requirements.txt

USER antony

CMD ["/bin/bash"]
