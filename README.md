# Microservice for a Social Media Analytics Platform

### Setup

1. Clone the project
2. Setup a virtual environment with Python v3.10
3. Install dependencies:
   ```
       pip install -r requirements.txt
   ```
4. Install and setup mongo db client, instructions for (mac)[https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/]
5. Run using:
   ```
   python -m flask run
   ```
6. curl to create post:
   curl --location 'http://localhost:5000/api/v1/posts/' \
   --header 'Content-Type: application/json' \
   --data '{"content": "This is an example post."}'
7. curl to get post analytics:
   curl --location 'http://localhost:5000/api/v1/posts/<post_id>/analysis/'
   Use post_id returned from the POST call.

### Scalability Considerations:

1. Large amounts of post data is handled by using asynchronous database writes using `multiprocessing.Process`. High request volumes is handled using `functools.lru_cache`, this can be built upon to use more sophisticated caching mechanisms such as using redis.
2. The analysis computation can be split into parallel tasks using text chunking, which is implemented in this application, some advanced methods can also be used in future to scale up such as MapReduce.

### Infrastructure Considerations

1. How would you handle the database?
   NoSQL, because data is unstructured in nature.

2. How would you manage traffic spikes?
   We can do horizontal scaling of our service which involves adding more instances (servers) to our application to handle increased load. We can utilize auto-scaling groups to automatically adjust the number of instances based on predefined scaling policies.
   Additionally we can use Application Load Balancers to distribute incoming application traffic across multiple targets, such as EC2 instances, containers, or IP addresses.

3. How would you ensure high availability and fault tolerance for the service?
   To ensure high availability we can do data replication across different servers or clusters to ensure redundancy and use load balancers to distribute incoming traffic across these instances to prevent a single point of failure. Additionally, we'll regularly back up critical data and implement a robust data recovery strategy.

4. How would you ensure the security of the data?
   Using proper authentication and authorization methods, keeping the service behind an API gateway and leveraging the API Gateway's authentication features to control and manage access to APIs based on user roles and permissions.

5. How would you handle logging, monitoring, and alerting for the service?
   Logging is implemented in the application using the `logging` module, logs can be directed to a service like splunk or wavefront for monitoring and observability. Alerts can be set up for low availability, high error count, high latencies etc.
   Additionally we can enable logging of API requests and responses to track potential security incidents and monitor for abnormal behavior and integrate the API Gateway with monitoring tools to receive alerts and notifications about security events or performance issues.

6. Which hosting providers and services would you consider using and why?
   Amazon Web Services would be a good choice, because of its high scalability, global reach, security and compliance, ecosystem and many other benefits.
