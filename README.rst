ficklefav
=========

I created ficklefav because reordering your favourites in gconfeditor is waaay
too cumbersome and because I wanted to practice writing clojure. Unfortunately,
I don't remember much about building GUIs in Java. So I decided to try
something else new... Jython.

FickleFav is a very basic application. It loads buttons for each icon in your netbook-launcher favourites list. You can click on a button and then click another button to swap their positions. There is a menu to save your changes and to restart netbook-launcher to see results.

FickleFav can only handle png icons. Since many icons are svg, (but I wanted to avoid depending on batik) FickleFav converts non-png icons using Imagemagick. 

Prerequisites
=============

ficklefav requires:

::

    jython >= 2.2.1-2ubuntu4
    imagemagick >= 7:6.5.7.8-1ubuntu1


Quick Setup
===========

:: 

    sudo apt-get install jython imagemagick
    jython ficklefav.py
