from flask import Response, Flask, request
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)

_INF = float("inf")


app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('alecrin_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))

@app.route("/")
def hello():
    start = time.time()
    graphs['c'].inc()
    
    time.sleep(0.600)
    end = time.time()
    graphs['h'].observe(end - start)

    
    return "Hello World!"

# @app.route("/metrics")
# def requests_count():
#     res = []
#     for k,v in graphs.items():
#         res.append(prometheus_client.generate_latest(v))
#     return Response(res, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)