from flask import Flask, request
from prometheus_client import Counter, Gauge, Histogram, Summary
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import time

# Cria um aplicativo Flask
app = Flask(__name__)

# Define as métricas
REQUEST_COUNTER = Counter(
    'request_counter', 'Total number of HTTP requests', ['method', 'endpoint']
)
ACTIVE_REQUESTS = Gauge(
    'active_requests', 'Number of active HTTP requests'
)
RESPONSE_TIME = Histogram(
    'response_time', 'HTTP response time in seconds', ['method', 'endpoint']
)
REQUEST_LATENCY = Summary(
    'request_latency', 'HTTP request latency in seconds', ['method', 'endpoint']
)

# Define um endpoint simples
@app.route('/')
def index():
    return 'Hello, world!'

# Define um endpoint com uma latência aleatória (para fins de demonstração)
@app.route('/random')
def random():
    with REQUEST_LATENCY.labels('GET', '/random').time():
        time.sleep(0.5)
        return 'This took a while'

# Define um handler que registra métricas para cada request
@app.before_request
def before_request():
    ACTIVE_REQUESTS.inc()
    REQUEST_COUNTER.labels(request.method, request.path).inc()

# Define um handler que registra métricas após cada request
@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    RESPONSE_TIME.labels(request.method, request.path).observe(response.response_time)
    REQUEST_LATENCY.labels(request.method, request.path).observe(response.response_time)
    return response

# Define um ponto de entrada para o servidor WSGI
application = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})

# Inicia o servidor
if __name__ == '__main__':
    run_simple('localhost', 5000, application)