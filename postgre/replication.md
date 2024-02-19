Starting with Postgres 10, logical replication is built into Postgres! This is often a better solution than external solutions. The Postgres docs are great and easy to follow. It's very easy. See the quick setup docs, which in essense boils down to running this:

```
-- On publisher DB
CREATE PUBLICATION mypub FOR TABLE users, departments;

-- On subscriber DB
CREATE SUBSCRIPTION mysub CONNECTION 'dbname=foo host=bar user=repuser' PUBLICATION mypub;
```
