#! /usr/bin/env jython

import sys
import os
import re
import glob

import javax.swing as sw
import java.awt as aw
from java.lang import Runtime
from java.io import *


DEFAULT_ICON = '/usr/share/pixmaps/apple-red.png'

class IconButton(object):
    def __init__(self, owner, app, iconPath):
        self.app = app

        i = sw.ImageIcon(iconPath)
        self.button = sw.JButton(i)
        self.button.setToolTipText(iconPath.split('/')[-1].split('.')[0]) # hack to get the app name

        listner = Clicker(owner, self)
        self.button.addActionListener(listner)

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

class Icon(object):
    def __init__(self, icon):
        """
        Constructor.

        icon -- The path to the provided icon
        """
        assert icon is not None
        self.icon = icon

        self.icon = self._validate_icon(icon)


    def _validate_icon(self, icon):
        if icon[0] != os.sep:
            # no absolute path
            icon = self._find_icon(icon)
        assert icon[0] == os.sep, 'we need a full path for %s' % icon

        if not icon.endswith('.png'):
            print 'WARNING: Converting %s to png' % icon
            icon = self._convert_to_png(icon)

        return icon


    def _convert_to_png(self, filename):
        app = os.path.basename(filename) + '.png'
        tempdir = tempfile.gettempdir()
        newfile = os.path.join(tempdir, 'netbook-launcher-fav-' + app)
        os.system('/usr/bin/convert -resize x32 '+ filename + ' ' + newfile)
        return newfile

    def _check_icon_exists(self, iconpath):
        # don't have a full path, we need to find the icon
        possibilities = glob.glob(iconpath)
        for i in possibilities:
            if i.endswith('.png'):
                return i, possibilities
        return None, possibilities

    def _find_icon(self, app):
        # We were only given a name, so assume it's in the pixmaps
        betterIcon, possibilities = self._check_icon_exists('/usr/share/pixmaps/' + app + '*')
        if betterIcon:
            return betterIcon

        # no png available, try gnome
        gnome = '/usr/share/icons/gnome/32x32/apps/' + app + '.png'
        betterIcon, gnomeOptions = self._check_icon_exists(gnome)
        if betterIcon:
            print 'WARNING: Cannot find icon', app
            print '\t attempting gnome icon'
            return betterIcon

        # pass on one of the non png images
        if possibilities:
            return possibilities[0]
        else:
            if gnomeOptions:
                return gnomeOptions[0]
            return app


class FickleFav(sw.JFrame):
    """
    This class represents the favourite picker window.
    """

    def __init__(self):
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
        gtool = GconfTool()
        buttons = []
        for app in gtool.get_app_list():
            icon = gtool.get_app_icon(app)
            if not icon:
                print 'WARNING: using default icon', DEFAULT_ICON
                icon = DEFAULT_ICON
            i = Icon(icon)
            icon = i.icon
            buttons.append( IconButton(self, app, icon) )

        return buttons


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
        faves = [b.app for b in self.buttonList]
        gtool = GconfTool()
        gtool.write_favorites(faves)


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
        self._favorites_list = self._fav + "favorites_list"
        self._favListType = ' --type=list --list-type=string '
        self._icon_regex = re.compile("Icon=(.*)$")

    def _get(self, key):
        cmd = self._gtool + " --get " + key
        return self._gconftool(cmd)

    def _set(self, key, ktype, value):
        cmd = self._gtool + " --set " + ktype + key + ' ' + value
        return self._gconftool(cmd)

    def _gconftool(self, cmd):
        p = Runtime.getRuntime().exec(cmd)
        output = p.getInputStream()
        return _get_first_string(output)

    def get_app_list(self):
        faves = self._get(self._favorites_list)
        faves = faves.strip('[]')
        return faves.split(',')

    def get_app_icon(self, app):
        icon = "."
        desktop = self._get(self._fav + app + "/desktop_file")
        try:
            for line in open(desktop, 'r'):
                match = self._icon_regex.search(line)
                if match:
                    return match.group(1)
        except:
            # TODO: Should I do something special here?
            #
            # probably was an IOError. for some reason, if we catch by type,
            # the IOError slips past.
            # Since we don't have a legit desktop file, do nothing and maybe we
            # get skipped.
            return

    def write_favorites(self, favorites):
        faves = ','.join(favorites)
        faves = '[' + faves + ']'
        self._set(self._favorites_list, self._favListType, faves)



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
