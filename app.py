
if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    from pathlib import Path  # python3 only
    load_dotenv(verbose=True)
    env_path = Path('..') / '.env'
    load_dotenv(dotenv_path=str(env_path))

    # Necessary fallback
    import os
    if os.environ['FLASK_APP'] is None:
        os.environ['FLASK_APP'] = 'quantum3d'

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

    printer_app.run(host='0.0.0.0', port=80,
                    debug=True, use_reloader=False, threaded=True)

    # Used alongside socket
    # TODO: add socket
    print('-> App is now running! <-')
