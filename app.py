
if __name__ == '__main__':
    # (TEST FOR NOW) Add root project directory to system paths / put here or in quantum3d/__init__.py?
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    print('realpath: ', os.path.dirname(os.path.realpath(__file__)))
    # TODO: Maybe also need to set PYTHONPATH!
    # TODO: SHOULD CREATE A PRINT SERVICE, CLASS OR SOMETHING! (WHAT? :D)
    # TODO: SHOULD HAVE AN EXCEPTION CLASS!
    # TODO: what if we implement Socket, but still use app.run?! will sockets work in that way?

    # Main app
    from quantum3d import printer_app
    printer_app.config.update(
        SECRET_KEY='T|-|E @R|<@M |<N|G|-|T'
    )

    # Run chromium if wasn't on windows
    if os.environ['DEV_ENV'].lower() != 'windows':
        print('-> On raspberry pi')
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
    socketio.run(printer_app,
                 host='0.0.0.0',
                 port=80,
                 debug=True,
                 use_reloader=False)
