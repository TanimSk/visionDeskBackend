# Guide

### Create a virtual environment

```bash
python -m venv env
```

### Install dependencies

```bash
pip install -r requirements.txt
cd vision_desk_backend
```

#### Run the server locally
```
python manage.py runserver
```

### For exposing IP
```bash
python manage.py runserver 0.0.0.0:<port>
```

### Run the worker (For updating the frames and annotations)
```bash
python worker.py
```

### You are good to go!