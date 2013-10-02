# Customize this to your setup
PYTHON = /usr/local/bin/python
APPENGINE = /usr/local/google_appengine
APP_IDENTIFIER = your_app_identifier

all:
	@echo "See Makefile for options."

run:
	@echo Running app...
	$(PYTHON) $(APPENGINE)/dev_appserver.py app \
		--require_indexes

deploy:
	@echo Uploading app...
	$(PYTHON) $(APPENGINE)/appcfg.py \
		--noauth_local_webserver --oauth2 \
		--application=$(APP_IDENTIFIER) \
		update app
