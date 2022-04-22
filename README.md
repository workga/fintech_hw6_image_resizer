# Image Resizer API

This API allows you to scale images.
You send a square image of any size, and the application will save it and its copies in sizes 32x32 and 64x64.
You can track the status of the task and get the result when the task is completed.

## Features

- Uses Redis to store images and tasks
- Uses python-rq for the task queue
- Three docker containers for application, Redis and workers

## Preparation

Create venv:
```bash
make venv
```

Build docker images:
```bash
make docker-build
```

## Running

Run docker containers:
```bash
make docker-run
```

You can also run the app without redis (so it won't work correctly).
Run application:
```bash
make up
```

## Usage

Send a jpeg image in the body of the POST request to this endpoint:
```
/resizer/tasks
```

You'll receive the task id and status in response:
```json
{
    "task_id": 1,
    "task_status": "queued"
}
```

Use this id to track the status of task using this endpoint:
```
/resizer/tasks/{task_id}
```

When the status is "finished", you can get the result.
Use the 'size' query parameter to choose the size: original, 32, 64 (default size is 32).
Use this endpoint to get an image in the response body:
```
/resizer/tasks/{task_id}/image?size=64x64
```

## API documentation

You can see API documentation in swagger using url:
```
/docs
```

## Development

Run tests:
```bash
make test
```

Run linters:
```bash
make lint
```

Run formatters:
```bash
make format
```