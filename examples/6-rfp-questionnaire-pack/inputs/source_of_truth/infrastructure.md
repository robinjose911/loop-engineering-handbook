# Infrastructure & Availability

Source id: `SRC-INFRA`

- Production runs in three availability zones in a single region.
- We target 99.9% monthly uptime.
- Backups are taken every 6 hours and tested monthly.
- Infrastructure is provisioned as code and peer-reviewed.
- We use a CDN with DDoS protection at the edge.
- Autoscaling is configured for all stateless services.
- Database failover is automated with a standby replica.
- All servers are patched on a 30-day cadence.
- Logs are centralized and retained for one year.
- Capacity is reviewed weekly against demand forecasts.
