from prometheus_client import Counter, Gauge, Histogram


incidents_created = Counter(
    "incidents_created",
    "Total number of incidents created",
    ["severity"],
)


incidents_active = Gauge(
    "incidents_active",
    "Number of currently open incidents",
    ["severity"],
)

incident_resolution_seconds = Histogram(
    "incident_resolution_duration_seconds",
    "Time from incident creation to resolution",
    ["severity"],
    buckets=(60, 300, 900, 1800, 3600, 7200, 14400, 28800, 86400, 172800),
)
