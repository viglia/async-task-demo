## Building the docker images

**task-service** (the rest service used to manage the jobs)

1. `cd` into `task_management_project` and run:

```
docker build -t django_service .
```

**job_consumer** (the rabbitmq consumer of the worker queue)

1. `cd` into `task_executor` and run:

```
docker build -t job_consumer .
```

## Creating a bridge network

1. create a network that will be used by the containers

```
docker network create  --driver bridge custom
```

## How to run the system in docker

1. start a `rabbitmq` broker

```
docker run --rm -it --hostname my-rabbit -p 15672:15672 -p 5672:5672 --network custom --name rabbit rabbitmq:3-management
```

2. start a `task_executor` (`job_consumer` image)

```
docker run --rm -it --network custom job_consumer job_queue -rhs rabbit -hs task-service
```

3. start the `task-service` (`django_task` image)

```
docker run --rm -it --network custom --name task-service -p 8000:8000  -e docker_rabbit_host='rabbit' django_service
```

### Some useful endpoints

It's possible to take advantage of the browsable API

1. create a new job or list existing ones: `http://127.0.0.1/api/jobs`
2. get the details of a specific job or update some information: `http://127.0.0.1/api/jobs/<int:pk>`


## Testing in Docker

1. make sure you have a rabbitmq broker running following point `1` of the section *"How to run the system in docker"* 
2. start a `task_executor` (`job_consumer` image) with a timeout of 2 seconds
```
docker run --rm -it --network custom job_consumer job_queue -rhs rabbit -hs task-service -to 2
```
3. run the tests with
```
docker run --rm -it --network custom --name task-service --entrypoint python -p 8000:8000  -e docker_rabbit_host='rabbit' django_service -m pytest --liveserver task-service:8000
```
