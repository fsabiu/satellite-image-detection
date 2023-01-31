# sat-image-detection
Repo to detect objects in satellite images - Back End


### Requirements

Python >= 3.7.x     
pip (python package manager)


### Installation & start
```bash
cd python-webapp
pip install -r requirements #or upgrade

nohup python webapp-flask_multithread_9001.py > logs/webapp9001_$(date "+%Y.%m.%d-%H.%M.%S").log 2>&1 &

```

Note: default port is 9001


### Usage
Some calls examples:
* localhost:9001/detect - detect objects in an image.
* localhost:9001/createModel - create new detection model based in YOLOv5.

Info about all the Web-app endpoints:

Please refer to [this swagger](http://130.61.157.94:9001/api/doc#/)


### Logs info

```bash
cd python-webapp/logs
tail -f webapp9001_2022.12.28-20.04.49.log
```
