#!/usr/bin/python
import sys, os, urllib
from gi.repository import Gtk, WebKit

webView = None
def refresh(widget, event):
    global webView
    webView.load_uri(webView.get_uri())

def HandleTitleChanged(webview, title):
    parent = webview
    while parent.get_parent() != None:
        parent = webview.get_parent()
    parent.set_title(title)
    return True

def HandleCreateWebView(webview, frame):
    info = Gtk.Window()
    info.set_default_size(1000, 700)
    child = WebKit.WebView()
    child.connect('create-web-view', HandleCreateWebView)
    child.connect('close-web-view', HandleCloseWebView)
    child.connect('navigation-policy-decision-requested', HandleNavigationRequested)
    #child.connect('notify::title', HandleTitleChanged)
    info.set_title('')
    info.add(child)
    info.show_all()
    return child

def HandleCloseWebView(webview):
    parent = webview
    while parent.get_parent() != None:
        parent = webview.get_parent()
    parent.destroy()

def HandleNewWindowPolicyDecisionRequested(webview, frame, request, navigation_action, policy_decision):
    if '&URL=' in request.get_uri():
        os.system('xdg-open "%s"' % urllib.unquote(request.get_uri().split('&URL=')[1]).decode('utf8'))

def HandleNavigationRequested(webview, frame, request, navigation_action, policy_decision):
    if '&URL=' in request.get_uri():
        HandleCloseWebView(webview)
        return 1

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print '\n\t%s <url> [user-agent] [user-stylesheet-uri]\n' % sys.argv[0]
        exit(1)

    url = sys.argv[1]
    user_agent = None
    stylesheet = None
    if len(sys.argv) > 2:
        user_agent = sys.argv[2]
    if len(sys.argv) > 3:
        stylesheet = 'file://localhost%s' % sys.argv[3]

    win = Gtk.Window()
    win.set_default_size(1500, 900)
    overlay = Gtk.Overlay()
    webView = WebKit.WebView()
    webView.load_uri(url)
    overlay = Gtk.Overlay()
    overlay.add(webView)

    # Apply Settings
    settings = WebKit.WebSettings()
    if user_agent:
        settings.set_property('user-agent', user_agent)
    settings.set_property('enable-spell-checking', True)
    if stylesheet:
        settings.set_property('user-stylesheet-uri', stylesheet)
    webView.set_settings(settings)

    # Add Signal handlers to the webview
    webView.connect('create-web-view', HandleCreateWebView)
    webView.connect('close-web-view', HandleCloseWebView)
    webView.connect('new-window-policy-decision-requested', HandleNewWindowPolicyDecisionRequested)
    webView.connect('navigation-policy-decision-requested', HandleNavigationRequested)
    #webView.connect('notify::title', HandleTitleChanged)
    win.set_title('')

    # Add the Refresh button
    fixed = Gtk.Fixed()
    fixed.set_halign(Gtk.Align.START)
    fixed.set_valign(Gtk.Align.START)
    overlay.add_overlay(fixed)
    fixed.show()
    image = Gtk.Image()
    image.set_from_pixbuf(Gtk.IconTheme().load_icon('gtk-refresh', 10, 0))
    imgevent = Gtk.EventBox()
    imgevent.add(image)
    imgevent.connect('button-press-event', refresh)
    fixed.put(imgevent, 10, 10)

    win.add(overlay)
    win.show_all()
    win.connect('destroy', Gtk.main_quit)
    Gtk.main()

