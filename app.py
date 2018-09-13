
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

    from quantum3d import printer_app
    printer_app.run(host='0.0.0.0', port=80,
                    debug=True, use_reloader=False, threaded=True)
