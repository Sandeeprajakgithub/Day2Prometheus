from flask import Flask, jsonify, request
import time
import random
from prometheus_client import start_http_server, Counter, Histogram

app = Flask(__name__)

# ------------------ METRICS ------------------

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status', 'status_class']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['endpoint'],
    buckets=[0.1, 0.3, 0.5, 1, 2, 3, 5]   # 👈 IMPORTANT for Grafana
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP Errors',
    ['endpoint', 'error_type']
)

# ------------------ HELPER ------------------

def track_metrics(endpoint, status_code):
    status_class = f"{status_code // 100}xx"

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(status_code),
        status_class=status_class
    ).inc()

# ------------------ ROUTES ------------------

@app.route('/')
@REQUEST_LATENCY.labels(endpoint="/").time()
def home():
    track_metrics("/", 200)
    return "Hi Welcome to Cloud SRE Adda"


# ------------------ DELAY ROUTES ------------------

@app.route('/delay/<int:seconds>')
@REQUEST_LATENCY.labels(endpoint="/delay").time()
def delay(seconds):
    delay_time = min(seconds, 3)
    time.sleep(delay_time)

    track_metrics("/delay", 200)
    return f"Response delayed by {delay_time} seconds"


@app.route('/random-delay')
@REQUEST_LATENCY.labels(endpoint="/random-delay").time()
def random_delay():
    delay_time = random.uniform(0.5, 3)
    time.sleep(delay_time)

    track_metrics("/random-delay", 200)
    return f"Random delay: {round(delay_time, 2)}s"


# ------------------ ERROR ROUTES ------------------

@app.route('/error/400')
def bad_request():
    track_metrics("/error/400", 400)
    ERROR_COUNT.labels('/error/400', 'BadRequest').inc()
    return jsonify({"error": "Bad Request"}), 400


@app.route('/error/404')
def not_found():
    track_metrics("/error/404", 404)
    ERROR_COUNT.labels('/error/404', 'NotFound').inc()
    return jsonify({"error": "Not Found"}), 404


@app.route('/error/500')
def internal_error():
    track_metrics("/error/500", 500)
    ERROR_COUNT.labels('/error/500', 'InternalServerError').inc()
    return jsonify({"error": "Internal Server Error"}), 500


# ------------------ EXCEPTION ROUTE ------------------

@app.route('/exception')
@REQUEST_LATENCY.labels(endpoint="/exception").time()
def exception():
    track_metrics("/exception", 500)
    ERROR_COUNT.labels('/exception', 'Exception').inc()
    raise Exception("Simulated application crash")


# ------------------ RANDOM FAILURE ------------------

@app.route('/random-failure')
@REQUEST_LATENCY.labels(endpoint="/random-failure").time()
def random_failure():
    if random.random() < 0.3:
        track_metrics("/random-failure", 500)
        ERROR_COUNT.labels('/random-failure', 'RandomFailure').inc()
        return "Random Failure Occurred", 500
    else:
        track_metrics("/random-failure", 200)
        return "Success"


# ------------------ HEALTH CHECK ------------------

@app.route('/health')
def health():
    track_metrics("/health", 200)
    return {"status": "UP"}, 200


# ------------------ MAIN ------------------

if __name__ == '__main__':
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)