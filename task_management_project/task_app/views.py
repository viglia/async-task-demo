from datetime import timedelta
import random

from django.conf import settings
from django.utils import timezone

import pika
from rest_framework import generics
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from task_app.models import Job
from task_app.serializers import JobSerializer


class JobList(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_sleep_time(self):
        return random.randint(15, 45)

    def get_queue_name(self):
        return settings.RABBITMQ["QUEUE"]

    def get_host(self):
        return settings.RABBITMQ["HOST"]

    def send_message(self, message_body):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.get_host()))
        channel = connection.channel()
        queue_name = self.get_queue_name()

        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=message_body)
        connection.close()

    def recent_job_exists(self, object_id):
        jobs = Job.objects.filter(
                object_id=object_id,
                created_at__gte=timezone.now() - timedelta(minutes=5)
        )
        return (jobs.exists(), jobs)

    def post(self, request: Request, *args, **kwargs):
        serializer = JobSerializer(data=request.data)
        # check if a job with the same object_id
        # has been already created in the last 5 minutes
        if serializer.is_valid():
            object_id = serializer.data['object_id']
            exists, jobs = self.recent_job_exists(object_id)
            # in that case, just return that job details
            if exists:
                job = JobSerializer(jobs[0])
                return Response(job.data)
        # otherwise create a new job
        request.data._mutable = True
        request.data["sleep_time"] = self.get_sleep_time()
        request.data._mutable = False

        response: Response = super().post(request, *args, **kwargs)
        # if the job was created succesfully send a message to the work queue
        if response.status_code == status.HTTP_201_CREATED:
            json = JSONRenderer().render(response.data)
            self.send_message(json)
        return response


class JobDetail(generics.RetrieveUpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def patch(self, request, *args, **kwargs):
        job_object = self.get_object()
        serializer = JobSerializer(job_object, data=request.data, partial=True)
        if serializer.is_valid():
            job_status = serializer.validated_data["job_status"]
            if job_status == "ST" or job_status == "RS":
                serializer.save(started_at=timezone.now())
            else:
                serializer.save()
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
