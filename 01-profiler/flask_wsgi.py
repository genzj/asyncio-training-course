# -*- encoding: utf-8 -*-
from flask_app import app
from werkzeug.contrib.profiler import ProfilerMiddleware

if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = ProfilerMiddleware(
        app,
        # profile_dir='.'
    )
    run_simple('127.0.0.1', 5000, app, use_debugger=True)
