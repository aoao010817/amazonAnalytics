FROM python:3

RUN apt-get update && apt-get install -y unzip

# Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_107.0.5304.87-1_amd64.deb
RUN apt-get install -y -f ./google-chrome-stable_107.0.5304.87-1_amd64.deb

# ChromeDriver
ADD https://chromedriver.storage.googleapis.com/107.0.5304.62/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && unzip chromedriver_linux64.zip

# Python
RUN pip install --upgrade pip &&\
  pip install selenium &&\
  pip install beautifulSoup4 &&\
  pip install pandas &&\
  pip install chromedriver_binary==107.*