#! /usr/bin/env jython

import sys
import os
import re
import glob

import javax.swing as sw
import java.awt as aw
from java.lang import Runtime
from java.io import *


class IconButton(object):
    def __init__(self, owner, iconPath):
        i = sw.ImageIcon(iconPath)
        self.button = sw.JButton(i)

        listner = Clicker(owner, self)
        self.button.addActionListener(listner)

        # hack to get the app name
        self.app = iconPath.split('/')[-1].split('.')[0]

class Clicker(aw.event.ActionListener):
    def __init__(self, owner, button):
        self.owner = owner
        self.button = button

    def actionPerformed(self, evt):
        self.owner.activate(self.button)

class ProxyActionListener(aw.event.ActionListener):
    def __init__(self, action):
        self.action = action

    def actionPerformed(self, evt):
        self.action()


def add_dimensions(result, addhend):
    w = result.getWidth()
    h = result.getHeight()
    result.setSize( w+addhend.getWidth(), h+addhend.getHeight() )

def add_dimensions_horiz(result, addhend):
    w = result.getWidth()
    h = max( result.getHeight(), addhend.getHeight() )
    result.setSize( w+addhend.getWidth(), h )

class FickleFav(sw.JFrame):
    """
    This class represents the favourite picker window.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.setDefaultCloseOperation(sw.WindowConstants.EXIT_ON_CLOSE)
        self.hand = None

        self.setTitle("FickleFav")
        self._setup_menu()
        self.buttonList = self._get_initial_button_list()
        self._setup_buttons(self.buttonList)

        self._set_size_x(
            lambda x: x.getPreferredSize()
            , lambda d: self.setPreferredSize(d))
        self._set_size_x(
            lambda x: x.getMaximumSize()
            , lambda d: self.setMaximumSize(d))
        self._set_size_x(
            lambda x: x.getMinimumSize()
            , lambda d: self.setMinimumSize(d))


    def _setup_menu(self):
        menuBar = sw.JMenuBar()

        menu = sw.JMenu("Menu")

        menuItem = sw.JMenuItem("Write Favorites Order")
        menuItem.addActionListener(ProxyActionListener(self.post_fav))
        menu.add(menuItem)

        menuItem = sw.JMenuItem("Restart Netbook-launcher")
        menuItem.addActionListener(ProxyActionListener(self.restart_launcher))
        menu.add(menuItem)

        menuBar.add(menu)

        self.setJMenuBar(menuBar)

    def _set_size_x(self, getSizeFn, setSizeFn):
        d = aw.Dimension(0,100) # buttons are too dumb to set a good min size
        for b in self.buttonList:
            add_dimensions_horiz(d, getSizeFn(b.button))

        setSizeFn(d)

    def _setup_buttons(self, buttonList):
        iconPanel = sw.JPanel()

        pane = self.getContentPane()
        pane.setLayout(sw.BoxLayout(pane, sw.BoxLayout.X_AXIS))

        for b in buttonList:
            pane.add(b.button)

        self.getContentPane().revalidate()

    def _get_initial_button_list(self):
        # TODO: use GconfTool
        icons = [
            "/usr/share/icons/Faenza/apps/48/WorldOfGoo.png"
            , "/usr/share/icons/Faenza/apps/48/abiword.png"
            , "/usr/share/icons/Faenza/apps/48/akregator.png"
            , "/usr/share/icons/Faenza/apps/48/amarok.png"
            , "/usr/share/icons/Faenza/apps/48/amule.png"
            , "/usr/share/icons/Faenza/apps/48/AdobeReader.png"]

        return [IconButton(self, path) for path in icons]


    def set_hand(self, button):
        self.hand = button

    def activate(self, button):
        if self.hand is None:
            self.set_hand(button)
        else:
            self.swap_with_hand(button)
            self.hand = None

    def swap_with_hand(self, button):
        a = self.buttonList.index(button)
        b = self.buttonList.index(self.hand)
        self.buttonList[a] = self.hand
        self.buttonList[b] = button
        self._setup_buttons(self.buttonList)


    def post_fav(self):
        for b in self.buttonList:
            print b.app

    def restart_launcher(self):
        # Stupid old jython won't let me do this:
        #import subprocess
        #subprocess.call("killall netbook-launcher")
        #pid = subprocess.Popen(["netbook-launcher", ""]).pid

        os.system("killall netbook-launcher")
        Runtime.getRuntime().exec("/usr/bin/netbook-launcher")

def _get_first_string(inputStream):
    reader = BufferedReader( InputStreamReader(inputStream, "UTF-8") )
    return reader.readLine()

class GconfTool(object):
    """
    This class represents gconftool-2
    """
    def __init__(self):
        self._gtool = "/usr/bin/gconftool-2"
        self._fav = "/apps/netbook-launcher/favorites/"
        self._icon_regex = re.compile("Icon=(.*)$")

    def _get(self, cmd):
        getCmd = self._gtool + " --get " + cmd
        p = Runtime.getRuntime().exec(getCmd)
        output = p.getInputStream()
        return _get_first_string(output)

    def get_app_list(self):
        kvalue = self._get(self._fav + "favorites_list")
        kvalue = kvalue.strip('[]')
        return kvalue.split(',')

    def get_app_icon(self, app):
        icon = "."
        desktop = self._get(self._fav + app + "/desktop_file")
        for line in open(desktop, 'r'):
            match = icon_regex.search(line)
            if match:
                icon = match.group(1)

        if icon[0] == os.sep:
            # already a full path
            return icon
        else:
            # special function, we need to find the icon
            possibilities = glob.glob('/usr/share/pixmaps/' + icon + '.*')
            return possibilities[0]



def main():
    try:
        sw.UIManager.setLookAndFeel( sw.UIManager.getSystemLookAndFeelClassName())
    except: #UnsupportedLookAndFeelException e
        pass
        ## ignore exception

    fav = FickleFav()
    fav.setLocation(0, 0)
    fav.setVisible(True)

main()
