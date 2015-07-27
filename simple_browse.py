#!/usr/bin/python
import sys, os, urllib, argparse, base64, time, threading, re
from gi.repository import Gtk, WebKit, Notify

webView = None
def refresh(widget, event):
    global webView
    webView.reload()

window_title = ''
def HandleTitleChanged(webview, title):
    global window_title
    window_title = title
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

prefills = {}
submit = False
ignore_submit = []
def prefill_password(webview, frame):
    global prefills, submit
    should_ignore_submit = False
    dom = webview.get_dom_document()

    forms = dom.get_forms()
    for i in range(0, forms.get_length()):
        form = forms.item(i)
        elements = form.get_elements()
        is_form_modified = False
        for j in range(0, elements.get_length()):
            element = elements.item(j)
            element_name = element.get_name()
            if element_name in ignore_submit:
                should_ignore_submit = True
            for key in prefills.keys():
                if element_name == key:
                    if prefills[key].lower() == 'true':
                        element.set_checked(True)
                        is_form_modified = True
                    else:
                        element.set_value(prefills[key])
                        is_form_modified = True
        if is_form_modified and submit and not should_ignore_submit:
            form.submit()

def HandleMimeType(webview, frame, request, mimetype, policy_decision):
    print 'Requested decision for mimetype:', mimetype
    return True

stop_threads = False
search_notifys = []
def SearchNotify(webview):
    global stop_threads
    global window_title
    global search_notifys
    while True:
        if stop_threads:
            break
        dom = webview.get_dom_document()
        if not dom:
            continue
        body = dom.get_body()
        if not body:
            continue
        body_html = body.get_inner_html()
        if not body_html:
            continue
        for notice in search_notifys:
            msgs = list(set(re.findall(notice, body_html)))
            if len(msgs) > 0:
                for msg in msgs:
                    Notify.init(window_title)
                    msg_notify = Notify.Notification.new(window_title, msg, "dialog-information")
                    msg_notify.show()
                time.sleep(2) # Don't duplicate the notification
        time.sleep(2)

if __name__ == "__main__":
    parser_epilog = ("Example:\n\n"
    "./simple_browse.py https://owa.example.com --useragent=\"Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0\" --stylesheet=~/simple_browse/sample_styles/owa_style.css --username=<webmail username> --b64pass=\"<base64 encoded password>\" --forminput=trusted:true --submit --notify=PHNwYW4gY2xhc3M9Im53SXRtVHh0U2JqIj4oW1x3IF0rKTwvc3Bhbj4=\n\n"
    "This command will open Outlook Web Access, set the user agent to allow it to \nload using pipelight (for silverlight support), login to webmail, then apply a \ncustom css style to make webmail look like a desktop app. When new emails\narrive, notification will be sent to gnome-shell.\n")

    parser = argparse.ArgumentParser(description="Simple Browser: A simple webkit browser written in Python", epilog=parser_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--useragent", help="An optional user agent to apply to the main page")
    parser.add_argument("--stylesheet", help="An optional stylesheet to apply to the main page")
    parser.add_argument("--username", help="A username we'll try to use to sign in")
    parser.add_argument("--password", help="A password for signing in")
    parser.add_argument("--b64pass", help="An alternative b64 encoded password for sign on")
    parser.add_argument("--forminput", help="A form field name and value to prefill (seperated by a colon). Only one value for each key is allowed.", action='append')
    parser.add_argument("--submit", help="Submit the filled form when we've finished entering values", action="store_true")
    parser.add_argument("--ignore-submit", help="Ignore the submit if the form contains this key", action='append')
    parser.add_argument("--title", help="Title for the window")
    parser.add_argument("--notify", help="A regex search string, base64 encoded, which will display a notification when found, example: <span class=\"nwItmTxtSbj\">([\w ]+)</span>", action='append')

    args = parser.parse_args()
    url = args.url

    user_agent = None
    if args.useragent:
        user_agent = args.useragent
    stylesheet = None
    if args.stylesheet:
        stylesheet = 'file://localhost%s' % os.path.abspath(args.stylesheet)
    if args.username:
        prefills['username'] = args.username
    if args.b64pass:
        prefills['password'] = base64.b64decode(args.b64pass)
    elif args.password:
        prefills['password'] = args.password
    if args.submit:
        submit = True
    if args.forminput:
        for field in args.forminput:
            key, value = field.split(':')
            if key in prefills:
                parser.print_help()
                exit(1)
            prefills[key] = value
    if args.ignore_submit:
        ignore_submit.extend(args.ignore_submit)
    if args.notify:
        for notice in args.notify:
            search_notifys.append(base64.b64decode(notice))

    win = Gtk.Window()
    scrolled = Gtk.ScrolledWindow()
    win.set_default_size(1500, 900)
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
    webView.connect('mime-type-policy-decision-requested', HandleMimeType)
    webView.connect('load-finished', prefill_password)
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

    win.add(scrolled)
    scrolled.add(overlay)
    win.show_all()
    win.connect('destroy', Gtk.main_quit)
    if args.title:
        window_title = args.title
        win.set_title(args.title)
    if search_notifys:
        t = threading.Thread(target=SearchNotify, args=(webView,))
        t.start()
    Gtk.main()
    stop_threads = True

