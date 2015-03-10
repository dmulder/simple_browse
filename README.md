# Simple Browser

usage: simple_browse.py [-h] [--useragent USERAGENT] [--stylesheet STYLESHEET]
                        [--username USERNAME] [--password PASSWORD]
                        [--b64pass B64PASS] [--forminput FORMINPUT] [--submit]
                        url

positional arguments:
  url

optional arguments:
  -h, --help            show this help message and exit
  --useragent USERAGENT
                        An optional user agent to apply to the main page
  --stylesheet STYLESHEET
                        An optional stylesheet to apply to the main page
  --username USERNAME   A username we'll try to use to sign in
  --password PASSWORD   A password for signing in
  --b64pass B64PASS     An alternative b64 encoded password for sign on
  --forminput FORMINPUT
                        A form field name and value to prefill (seperated by a
                        colon). Only one value for each key is allowed.
  --submit              Submit the filled form when we've finished entering
                        values

Example:

./simple_browse.py https://owa.example.com --useragent="Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0" --stylesheet=~/simple_browse/sample_styles/owa_style.css --username=<webmail username> --b64pass="<base64 encoded password>" --forminput=trusted:true --submit

This command will open Outlook Web Access, set the user agent to allow it to load using pipelight (for silverlight support), login to webmail, then apply a custom css style to make webmail look like a desktop app.
