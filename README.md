# API Gateway

An API gateway that leverages python to create a RESTful admin API and Node.js as a gateway, forwarding request to other API services.

#### Features

- Forwards API requests based on regular expressions and URL rewrites
- Rate limiting
    - Based on IP or API key.
    - Separate rates per API endpoint for anonynous and authenticated requests.
    - Uses Redis
- API key based authentication
- Bans
   - Bans are based on CIDR notation (ex 76.87.0.0/16, also used in AWS security groups), allowing bans based on IP blocks.
- Logging
   - Logs to stdout which can be captured by CloudWatch Logs and other log agents.
- Analytics
   - Requests are sent to SQS and aggregated to minute resolution, available in a postgres table for analytics.
- Admin REST API
   - Exposes
      - Bans
      - API Keys
      - Analytics (ROADMAP)
      - Users (to power admin UI)
      - Sessions (to power admin UI)
  - Powered by [restful-ben](https://github.com/CityOfPhiladelphia/restful-ben)

### Usage

Endpoint config file

```yaml
endpoints:
  - name: myapi
    pattern: /myapi/v1(/.*)
    target: http://localhost:8085$1
    rateLimit:
      anonymous:
        windowMs: 60000 # 1 minute
        max: 100 # 100 requests per window
      authenticated:
        windowMs: 60000 # 1 minute
        max: 300 # 300 requests per window
```

To run locally using Docker, clone this repo and run:

`docker-compose up`