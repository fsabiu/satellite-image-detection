# satellite-image-detection
Back end of a web application that detects objects in satellite images


### Requirements

Python >= 3.7.x     
pip (python package manager)


### Requirements installation
```bash
cd python-webapp
pip install -r requirements.txt
```

### Start

To execute the webserver in background and redirect the logs into the logs directory execute the following command:
```bash
nohup python webapp-flask_multithread_9001.py > logs/webapp9001_$(date "+%Y.%m.%d-%H.%M.%S").log 2>&1 &
```
Note: default port is 9001


### Usage
Some calls examples:
* [https://localhost:9001/detect](http://130.61.157.94:9001/api/doc#/Satellite%20images/sat.api.detect) - detect objects in an image.
* [https://localhost:9001/createModel](http://130.61.157.94:9001/api/doc#/Satellite%20images/sat.api.createModel)- create new detection model based in YOLOv5.

Info about all the Web-app endpoints:

Please refer to [this swagger](http://130.61.157.94:9001/api/doc#/)


### Logs info

```bash
cd python-webapp/logs
tail -f webapp9001_2022.12.28-20.04.49.log
```


### Run tests
Tests have been deployed in a table driven way.

e.g.
```rb
def test_getClasses(self): # Post
        """
        Test /getClasses function
        """
        testcases = [
            {
                "name": "Correct",
                "input": 
                {
                        "modelId": 0
                    }, 
                "expected": 'classes'
            },
            {
                "name": "Missing modelId", 
                "input": "", 
                "expected": 'modelId missing'
            },
            {
                "name": "Unexisting modelId",
                "input": {
                        "modelId": 9999
                    }, 
                "expected": '{}'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/getClasses", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )
```

To execute all tests just run
```bash
cd python-webapp/
python test.py
```

Output:
```
.............
----------------------------------------------------------------------
Ran 13 tests in 17.408s

OK
```
