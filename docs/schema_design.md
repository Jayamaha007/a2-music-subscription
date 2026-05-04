# DynamoDB Schema Design

## login table

| Attribute  | Type   | Role          |
|------------|--------|---------------|
| email      | String | Partition Key |
| user_name  | String | Attribute     |
| password   | String | Attribute     |

## music table

> TODO: analyse 2026a2_songs.json to confirm PK/SK, then document here.

### Key Schema
| Attribute | Type   | Role |
|-----------|--------|------|
| TBD       | String | Partition Key |
| TBD       | String | Sort Key |

### GSI — rationale
<!-- TODO: document GSI design and access patterns it supports -->

### LSI — rationale
<!-- TODO: document LSI design and access patterns it supports -->
