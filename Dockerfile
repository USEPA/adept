FROM python:3.9-rc-slim AS builder

RUN DEBIAN_FRONTEND=noninteractive apt-get update        &&\
    DEBIAN_FRONTEND=noninteractive apt-get -y install      \
      -qq -o=Dpkg::Use-Pty=0                               \
      apt-utils
      
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install      \     
      -qq -o=Dpkg::Use-Pty=0                               \
      build-essential                                      \
      gcc                                                  \
      gfortran                                             \
      libxml2-dev                                          \
      libxslt-dev                                          \
      python-dev                                         &&\
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install             \
   --no-cache-dir           \
   --compile                \
   -r requirements.txt
   
FROM python:3.9-rc-slim AS final

RUN DEBIAN_FRONTEND=noninteractive apt-get update        &&\
    DEBIAN_FRONTEND=noninteractive apt-get -y install      \
      -qq -o=Dpkg::Use-Pty=0                               \
      apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install      \
      -qq -o=Dpkg::Use-Pty=0                               \
      gnupg2                                               \
      wget                                                 \
      curl                                                 \
      xvfb                                                 \
      unzip

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -                    &&\
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list  &&\
    DEBIAN_FRONTEND=noninteractive apt-get update -y -qq -o=Dpkg::Use-Pty=0                               &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq -o=Dpkg::Use-Pty=0 google-chrome-stable         &&\
    wget -q -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip &&\
    unzip -qq /tmp/chromedriver.zip chromedriver -d /usr/local/bin                                        &&\
    chmod 755 /usr/local/bin/chromedriver                                                                 &&\
    rm -rf /tmp/chromedriver.zip                                                                          &&\
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV DISPLAY=:99
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
      
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

COPY ./scripts /scripts

ENTRYPOINT ["python", "/scripts/all_state_scraper.py"]
CMD ["default"]

