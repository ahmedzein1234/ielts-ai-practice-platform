import http from 'k6/http';
import { sleep, check } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp up
    { duration: '1m', target: 50 },  // Load test
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<250'], // 95% of requests must complete below 250ms
    http_req_failed: ['rate<0.01'],   // Error rate must be less than 1%
    errors: ['rate<0.01'],
  },
};

const baseUrl = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  const endpoints = [
    '/health',
    '/api/v1/auth/status',
    '/api/v1/speaking/questions',
    '/api/v1/writing/prompts',
  ];

  for (const endpoint of endpoints) {
    const response = http.get(`${baseUrl}${endpoint}`);
    
    const success = check(response, {
      [`${endpoint} status is 200`]: (r) => r.status === 200,
      [`${endpoint} response time < 250ms`]: (r) => r.timings.duration < 250,
      [`${endpoint} has valid JSON`]: (r) => {
        try {
          JSON.parse(r.body);
          return true;
        } catch {
          return false;
        }
      },
    });

    if (!success) {
      errorRate.add(1);
    }

    sleep(1);
  }
}

export function handleSummary(data) {
  return {
    'k6-smoke-results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const { metrics, root_group } = data;
  const { http_req_duration, http_req_failed, http_reqs } = metrics;
  
  return `
K6 Smoke Test Results
=====================

Requests:
  Total: ${http_reqs.count}
  Failed: ${http_req_failed.rate * 100}%

Response Times:
  Average: ${http_req_duration.avg.toFixed(2)}ms
  Median: ${http_req_duration.med.toFixed(2)}ms
  P95: ${http_req_duration.values['p(95)'].toFixed(2)}ms
  P99: ${http_req_duration.values['p(99)'].toFixed(2)}ms

Thresholds:
  P95 < 250ms: ${http_req_duration.values['p(95)'] < 250 ? '✅ PASS' : '❌ FAIL'}
  Error rate < 1%: ${http_req_failed.rate < 0.01 ? '✅ PASS' : '❌ FAIL'}
`;
}
