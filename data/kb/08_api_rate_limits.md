# API Rate Limits
The CloudNest REST API enforces per-plan rate limits measured in requests per minute (RPM).
Exceeding the rate limit returns HTTP 429 with a Retry-After header.
Exact included API call quotas per plan are tracked in the live pricing/usage system, since they are
adjusted based on current promotions and plan version.
