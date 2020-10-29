import argparse
import json
import pika
from pika.channel import Channel
from pika.spec import Basic
import requests
import signal
import time


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Consumer():
    def __init__(self, queue: str, rhost: str, host: str, timeout: int):
        self.queue = queue
        self.rhost = rhost
        self.host = host
        self.timeout = timeout

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def update_task_status(self, id, status):
        update_endpoint = f"http://{self.host}:8000/api/jobs/{id}"
        r = requests.patch(update_endpoint, data={"job_status": status})
        print(f"Status code: {r.status_code}")
        return r

    def callback(self, ch: Channel, method: Basic.Deliver, properties, body):
        print(f"Received: {body}"
              f"\nre-delivered: {method.redelivered}")
        job = json.loads(body)
        try:
            signal.signal(signal.SIGALRM, self.signal_handler)
            signal.alarm(self.timeout)   # Timeout seconds

            print(f"Job Started: {job['id']}")
            self.update_task_status(job['id'], 'RS' if method.redelivered
                                    else 'ST')

            time.sleep(job["sleep_time"])

            signal.alarm(0)
            print(f"Job Finished: {job['id']}")
            response = self.update_task_status(job['id'], 'EN')
            if response.status_code >= 400 and response.status_code <= 408:
                print("Error while saving: buffering results....")
                # do something to managhe such case

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except TimeoutException:
            print("Timed out!!")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            self.update_task_status(job['id'], 'DL')

    def start(self):
        print(f"Listening on queue: {self.queue}")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rhost))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue)

        channel.basic_consume(queue=self.queue,
                              on_message_callback=self.callback,
                              auto_ack=False)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Launches a consumer listening on [queue]"
        )
    parser.add_argument("queue", help="Name of the queue to listen on")
    parser.add_argument("--rhost", "-rhs",
                        help="the rabbitmq host",
                        default="127.0.0.1")
    parser.add_argument("--host", "-hs",
                        help="the task management service host",
                        default="127.0.0.1")
    parser.add_argument("--timeout", "-to",
                        help=("max number of seconds before the "
                              "job is cancelled"),
                        default=60,
                        type=int)

    args = parser.parse_args()
    c = Consumer(**vars(args))
    c.start()
