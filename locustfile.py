from locust import HttpLocust, TaskSet, task


class RequestBehavior(TaskSet):
    @task(1)
    def ping(self):
        self.client.get("http://localhost:8888/sleep")


class ExecuteRequests(HttpLocust):
    task_set = RequestBehavior
    min_wait = 5000
    max_wait = 9000
