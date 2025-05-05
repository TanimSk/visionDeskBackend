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

# NB: You must have redis server running in the background!
URL: https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-mac-os/

### Change stream the URL in `worker.py`, here `cap = cv2.VideoCapture("rtsp://192.168.1.112:8554/mystream")` 

### You are good to go!
