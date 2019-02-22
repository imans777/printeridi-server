
if __name__ == '__main__':
    # (TEST FOR NOW) Add root project directory to system paths / put here or in quantum3d/__init__.py?
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    # print('realpath: ', os.path.dirname(os.path.realpath(__file__)))
    # TODO: Maybe also need to set PYTHONPATH!
    # SHOULD CREATE A PRINT SERVICE, CLASS OR SOMETHING! (WHAT? :D) (for the prints to be organized)
    # SHOULD HAVE AN EXCEPTION CLASS!
    # what if we implement Socket, but still use app.run?! will sockets work in that way?

    # Main app
    from quantum3d import printer_app
    from quantum3d.db import pdb
    printer_app.config.update(
        SECRET_KEY='T|-|E @R|<@M |<N|G|-|T',
        UPLOAD_FOLDER=os.environ['UPLOAD_FOLDER']
    )

    # Run chromium if wasn't in development nor on windows and when lcd was requested
    if os.environ['FLASK_ENV'] != 'development' and os.environ['CUR_ENV'].lower() == 'rpi' and pdb.get_key('lcd'):
        print('-> starting chromium')
        import subprocess
        subprocess.Popen(["chromium-browser", "--disk-cache-dir=/dev/null",
                          "--disk-catch-size=1", "--hide-scrollbars",
                          "--overscroll-history-navigation=0", "--incognito",
                          "--disable-session-crashed-bubble", "--disable-infobars",
                          " --noerrdialog", "--no-sandbox",
                          "--kiosk", "--disable-translate",
                          "--start-maximized", "http://0.0.0.0"])

    # Used alongside socket
    from quantum3d import socketio
    print('-> App is now running! <-')

    # TODO: run `curl localhost` locally to see that the connection is active or not!
    # if it's not, the following should be checked:
    # - 'sudo ufw allow 80' for firewall!
    # - 'netstat -tupln | grep ":80"' to see if the server is really listening!
    # - 'iptables -I INPUT -p tcp --dport 80 -j ACCEPT' to let the packets through!

    # TODO: set debug to false
    # and run on gevent webserver for
    # high streaming, etc. enhancement!
    socketio.run(printer_app,
                 host='0.0.0.0',
                 port=80,
                 debug=True,
                 use_reloader=False)
