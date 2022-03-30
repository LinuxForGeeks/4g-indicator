#!/usr/bin/python3

import os
import signal
import subprocess
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GLib,  GdkPixbuf, Notify, AppIndicator3 as appindicator
from threading import Timer
from settings import Settings

APPINDICATOR_ID = '4gindicator'
WIFI_LIST = ['Redmi 9T', 'Téléphone Mi']
EXTRA_WIFI_LIST = ['D-Link-ELG']
AUTOCHECK_TIMEOUT = 10 # seconds
FLASH_RATE = 60 # seconds

class Indicator():

    def __init__(self):
        self.settings = Settings()
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, self.get_current_state_icon(), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        Notify.init(APPINDICATOR_ID)
        # Update status every x seconds
        self.flash_time_counter = 0
        GLib.timeout_add_seconds(AUTOCHECK_TIMEOUT, self.update_4g_state, True)

    def show_about_dialog(self, _):
        aboutdialog = Gtk.AboutDialog()

        authors = ['AXeL-dev']
        documenters = ['AXeL-dev']

        aboutdialog.set_program_name('4G AppIndicator for Ubuntu')
        aboutdialog.set_comments('AppIndicator to show 4G status.')
        aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(self.get_resource('4g.svg')))
        aboutdialog.set_authors(authors)
        aboutdialog.set_documenters(documenters)
        aboutdialog.set_website('https://github.com/LinuxForGeeks/4g-indicator')
        aboutdialog.set_website_label('Source code at GitHub')
        aboutdialog.connect('response', self.close_about_dialog)

        aboutdialog.show()

    def close_about_dialog(self, action, parameter):
        action.destroy()

    def get_resource(self, resource_name):
        return os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources'), resource_name)

    def get_current_state_icon(self):
        if self.get_current_4g_state() == True:
            icon_name = '4g-on.svg'
        else:
            icon_name = '4g-off.svg'
        return self.get_resource(icon_name)

    def get_icon_desc(self):
        return '4g-on' if self.status == True else '4g-off'

    def get_current_4g_state(self):
        try:
            output = subprocess.check_output('iwgetid -r', shell=True, stdin=subprocess.PIPE)
            self.status = output.decode().rstrip() in WIFI_LIST
        except subprocess.CalledProcessError as e:
            self.status = False
        return self.status

    def connect(self, widget, ssid):
        try:
            output = subprocess.check_output('nmcli -c no device wifi list --rescan yes && nmcli device wifi connect "{0}"'.format(ssid), shell=True, stdin=subprocess.PIPE)
            if 'successfully activated' in output.decode():
                self.update_4g_state()
        except subprocess.CalledProcessError as e:
            print(e)

    def build_menu(self):
        menu = Gtk.Menu()

        item_connect = Gtk.MenuItem.new_with_label('Connect')
        menu_connect = Gtk.Menu()
        item_connect.set_submenu(menu_connect)
        menu.append(item_connect)

        for ssid in WIFI_LIST + EXTRA_WIFI_LIST:
            item_connect_option = Gtk.MenuItem.new_with_label(ssid)
            item_connect_option.connect('activate', self.connect, ssid)
            menu_connect.append(item_connect_option)

        item_settings = Gtk.MenuItem.new_with_label('Settings')
        menu_settings = Gtk.Menu()
        item_settings.set_submenu(menu_settings)
        menu.append(item_settings)

        self.item_show_notifications = Gtk.CheckMenuItem.new_with_label('Show notifications')
        if self.settings.show_notifications:
            self.item_show_notifications.set_active(True)
        self.item_show_notifications.connect('activate', self.toggle_show_notifications)
        menu_settings.append(self.item_show_notifications)

        self.item_enable_flash = Gtk.CheckMenuItem.new_with_label('Enable flash')
        if self.settings.enable_flash:
            self.item_enable_flash.set_active(True)
        self.item_enable_flash.connect('activate', self.toggle_enable_flash)
        menu_settings.append(self.item_enable_flash)

        self.item_about = Gtk.MenuItem.new_with_label('About')
        self.item_about.connect('activate', self.show_about_dialog)
        menu.append(self.item_about)

        item_quit1 = Gtk.MenuItem.new_with_label('Quit')
        item_quit1.connect('activate', self.quit1)
        menu.append(item_quit1)

        menu.show_all()
        return menu

    def toggle_show_notifications(self, widget):
        self.settings.show_notifications = not self.settings.show_notifications
        self.settings.save()

    def toggle_enable_flash(self, widget):
        self.settings.enable_flash = not self.settings.enable_flash
        self.flash_time_counter = 0
        self.settings.save()

    def flash_on(self):
        self.indicator.set_icon_full(self.get_resource('4g-flash.svg'), '4g-flash')

    def flash_off(self):
        self.indicator.set_icon_full(self.get_resource('4g-on.svg'), '4g-on')
        if self.flash_number < 3:
            t = Timer(0.5, self.play_flash) 
            t.start()

    def play_flash(self):
        self.flash_number += 1
        self.flash_on()
        t = Timer(0.5, self.flash_off) 
        t.start()

    def update_4g_state(self, loop = False):
        old_status = self.status
        self.indicator.set_icon_full(self.get_current_state_icon(), self.get_icon_desc())
        if self.settings.enable_flash:
            self.flash_time_counter += AUTOCHECK_TIMEOUT
        if old_status != self.status:
            self.flash_time_counter = 0
            self.show_notification()
        elif self.status == True and self.settings.enable_flash and self.flash_time_counter == FLASH_RATE:
            self.flash_time_counter = 0
            self.flash_number = 0
            self.play_flash()
        if not loop:
            return False # Do not loop
        else:
            return True # Loop

    def show_notification(self):
        if not self.settings.show_notifications:
            return

        title = 'Notify'
        if self.status:
            title = '4G is enabled'
        else:
            title = '4G was disabled'

        self.notification = Notify.Notification.new(title)
        self.notification.show()

        # creates a timer to close the notification as the 'set_timeout' Notify method is ignored by the server.
        t = Timer(1.0, self.close_notification) 
        t.start()

    def close_notification(self):
        self.notification.close()

    def quit1(self, _):
        Notify.uninit()
        Gtk.main_quit()

if __name__ == '__main__':
    Indicator()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
