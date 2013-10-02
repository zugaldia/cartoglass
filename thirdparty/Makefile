PACKAGES = ../app/packages
CLIENT_VERSION = 1.2
REQUESTS_VERSION = 2.0.0

all:
	@echo See Makefile for options

download: download-python-client download-requests

clean: clean-python-client clean-requests

download-python-client:
	@echo Downloading Google APIs Client Library for Python...
	wget https://google-api-python-client.googlecode.com/files/google-api-python-client-gae-$(CLIENT_VERSION).zip > /dev/null 2>&1
	mkdir google-api-python-client-gae-$(CLIENT_VERSION)
	cd google-api-python-client-gae-$(CLIENT_VERSION); unzip ../google-api-python-client-gae-$(CLIENT_VERSION).zip > /dev/null
	rm google-api-python-client-gae-$(CLIENT_VERSION).zip
	cd $(PACKAGES); ln -s ../../thirdparty/google-api-python-client-gae-$(CLIENT_VERSION)/apiclient apiclient
	cd $(PACKAGES); ln -s ../../thirdparty/google-api-python-client-gae-$(CLIENT_VERSION)/httplib2 httplib2
	cd $(PACKAGES); ln -s ../../thirdparty/google-api-python-client-gae-$(CLIENT_VERSION)/oauth2client oauth2client
	cd $(PACKAGES); ln -s ../../thirdparty/google-api-python-client-gae-$(CLIENT_VERSION)/uritemplate uritemplate

clean-python-client:
	@echo Deleting Google APIs Client Library for Python...
	rm -rf google-api-python-client-gae-$(CLIENT_VERSION)
	rm -rf $(PACKAGES)/apiclient
	rm -rf $(PACKAGES)/httplib2
	rm -rf $(PACKAGES)/oauth2client
	rm -rf $(PACKAGES)/uritemplate

download-requests:
	@echo Downloading Requests...
	wget https://pypi.python.org/packages/source/r/requests/requests-$(REQUESTS_VERSION).tar.gz > /dev/null 2>&1
	tar zxf requests-$(REQUESTS_VERSION).tar.gz
	rm requests-$(REQUESTS_VERSION).tar.gz
	cd $(PACKAGES); ln -s ../../thirdparty/requests-$(REQUESTS_VERSION)/requests requests

clean-requests:
	@echo Deleting Requests...
	rm -rf requests-$(REQUESTS_VERSION)
	rm -rf $(PACKAGES)/requests
