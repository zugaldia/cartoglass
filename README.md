# CartoGlass

CartoGlass is a simple, well-documented, demo app which showcases some basic principles of the Mirror API.

It tries to remain as simple as possible while following good practices for App Engine and Google Glass development.

## Features

* It subscribes to timeline actions, and lets you play the "guess a number" game (between 1 and 10).
* It subscribes to location updates, and tracks every update in a [CartoDB](http://cartodb.com) database for easy visualization.

Some of the ideas illustrated in the code:

* Use Google APIs Client Library to interact with Google resources and perform the OAuth2 dance.
* Use Python Requests to insert data into CartoDB.
* Send cards to Glass.
* Subscribe to location and timeline notifications.
* Respond to user actions.
* Use of built-in menu items (stream video, view website, read aloud...) and custom items too.

Check out the comments in the code (the important file is `main.py`) for common issues and solutions.

Most main components of the Mirror API are used here, contacts and attachments are probably the two big ones we didn't include.

## Requirements

CartoGlass is Python code which runs on [App Engine](https://developers.google.com/appengine), but it was designed so that it's easy to adapt to other cloud services.

### Install

* Clone the repository in a folder of your choice:

```
$ git clone https://github.com/zugaldia/cartoglass.git
```

* Download and install the 3rd-party packages with the help of the included `Makefile`:

```
$ cd cartoglass/thirdparty
$ make download
```

* Copy `app/config.template.py` to `app/config.py` and add your (secret) keys:

You will obtain `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the [Google Console API](http://code.google.com/apis/console).
Go to [CartoDB](http://www.cartodb.com) to get a free `CARTODB_API_KEY`.

Et voilà, ready to run.

## About

CartoGlass was originally developed as companion code for my presentations during [DevFest DC](http://www.devfestdc.org) (October 2013) and [DevFest Madrid](http://www.devfestmadrid.com) (November 2013). 

### Video

The included demo video is one of the segments of a
[speed run of Final Fantasy II](http://archive.org/details/FinalFantasy2_356) completed on December 19, 2005.
It's available under a public domain license hosted by the Internet Archive. (I just needed a quick fun video.)

### License

See `LICENSE` file.
