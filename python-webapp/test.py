import http.client
import json
import ssl
import unittest

ssl._create_default_https_context = ssl._create_unverified_context

"""
Method	                Equivalent to
.assertEqual(a, b)	    a == b
.assertTrue(x)	        bool(x) is True
.assertFalse(x)	        bool(x) is False
.assertIs(a, b)	        a is b
.assertIsNone(x         x is None
.assertIn(a, b)	        a in b
.assertIsInstance(a, b)	isinstance(a, b)
"""

class TestWebapp(unittest.TestCase):
    port = 9001
    conn = http.client.HTTPSConnection("iccc-s019.pl.oracle.com", port)
    img_id_test = ""
    model_created = None 

    def test_getModels(self): # Get
        """
        Test /getModels function
        """
        testcases = [
            {
                "name": "Empty parameters", 
                "input": '', "expected": 'models'
            }
        ]

        for case in testcases:
            payload = case["input"]
            headers = {}
            self.conn.request("GET", "/getModels", payload, headers)
            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_createModel(self): # Get
        """
        Test /createModel function
        """
        testcases = [
            {
                "name": "Empty parameters", 
                "input": '', 
                "expected": 'modelId'
            }
        ]

        for case in testcases:
            payload = case["input"]
            headers = {}
            self.conn.request("GET", "/createModel", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.model_created = json.loads(actual)["modelId"]
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

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

    def test_detect(self): # Post
        """
        Test /detect function
        """

        # Correct
        with open('testdata/image1.txt', 'r') as file:
            imageData = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 0,
                        "imageData": imageData
                    }, 
                "expected": 'objects'
            },
            {
                "name": "Missing modelId",
                "input": 
                {
                        "imageData": imageData
                    }, 
                "expected": 'modelId required'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/detect", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_detectDiff(self): # Post
        """
        Test /detectDiff function
        """

        # Correct
        with open('testdata/image1.txt', 'r') as file:
            imageData1 = file.read()

        with open('testdata/image2.txt', 'r') as file:
            imageData2 = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 0,
                        "image1": imageData1,
                        "image2": imageData2
                    }, 
                "expected": 'objects'
            },
            {
                "name": "Missing image2",
                "input": 
                {
                        "image1": imageData1
                    }, 
                "expected": 'image2 missing'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/detectDiff", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_detectAllDiff(self): # Post
        """
        Test /detectAllDiff function
        """

        # Correct
        with open('testdata/image1.txt', 'r') as file:
            imageData1 = file.read()

        with open('testdata/image2.txt', 'r') as file:
            imageData2 = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 0,
                        "image1": imageData1,
                        "image2": imageData2
                    }, 
                "expected": 'objects'
            },
            {
                "name": "Missing image2",
                "input": 
                {
                        "image1": imageData1
                    }, 
                "expected": 'image2 missing'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/detectAllDiff", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_stitch(self): # Post
        """
        Test /stitch function
        """

        # Correct
        with open('testdata/image1.txt', 'r') as file:
            imageData1 = file.read()

        with open('testdata/image2.txt', 'r') as file:
            imageData2 = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 0,
                        "image1": imageData1,
                        "image2": imageData2
                    }, 
                "expected": 'result' # Image base 64
            },
            {
                "name": "Missing image2",
                "input": 
                {
                        "image1": imageData1
                    }, 
                "expected": 'image2 missing'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/stitch", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_detectSarDiff(self): # Post
        """
        Test /detectSarDiff function
        """

        # Correct
        with open('testdata/sar_image1.txt', 'r') as file:
            imageData1 = file.read()

        with open('testdata/sar_image2.txt', 'r') as file:
            imageData2 = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "image1": imageData1,
                        "image2": imageData2
                    }, 
                "expected": 'result' # Image base 64
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/detectSarDiff", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_addToTrainingSet(self): # Post
        """
        Test /addToTrainingSet function
        """

        # Correct
        with open('testdata/image1.txt', 'r') as file:
            imageData = file.read()

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 1,
                        "objects": [
                            {
                                "class": "Airplane",
                                "bounds": {
                                    "x1": 784,
                                    "x2": 898,
                                    "y1": 277,
                                    "y2": 411
                                }
                            },
                            {
                                "class": "oil-storage-tank",
                                "bounds": {
                                    "x1": 555,
                                    "x2": 895,
                                    "y1": 27,
                                    "y2": 411
                                }
                            }
                        ],
                        "image": imageData
                }, 
                "expected": 'imageId'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/addToTrainingSet", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            if "imageId" in json.loads(actual):
                self.img_id_test = json.loads(actual)["imageId"]
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_removeFromTrainingSet(self): # Post
        """
        Test /removeFromTrainingSet function
        """

        testcases = [
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 1,
                        "imageId": self.img_id_test
                }, 
                "expected": 'Success'
            },
            {
                "name": "Standard use case",
                "input": 
                {
                        "modelId": 1,
                        "imageId": "img_20221221131800658_1.png"
                }, 
                "expected": 'does not exist'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/removeFromTrainingSet", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")

            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )        

    def test_trainModel(self): # Post
        """
        Test /trainModel function
        """

        testcases = [
            {
                "name": "model already trained",
                "input": 
                {
                        "modelId": 1,
                        "trainingData": [1]
                }, 
                "expected": 'has already been used for the training'
            },
            {
                "name": "not existing model",
                "input": 
                {
                        "modelId": 9999,
                        "trainingData": [9999]
                }, 
                "expected": 'No data to fetch'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/trainModel", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            if "imageId" in json.loads(actual):
                self.img_id_test = json.loads(actual)["imageId"]
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_deleteModel(self): # Delete
        """
        Test /deleteModel function
        """
        testcases = [
            {
                "name": "deleting model 0",
                "input": 
                {
                        "modelId": 0
                    }, 
                "expected": 'Cannot delete model 0'
            },
            {
                "name": "deleting correct", 
                "input": self.model_created, 
                "expected": 'OK'
            },
            {
                "name": "Unexisting modelId",
                "input": {
                        "modelId": 9999
                    }, 
                "expected": 'No model number 9999'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("DELETE", "/deleteModel", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )

    def test_getStatus(self): # Post
        """
        Test /getStatus function
        """

        testcases = [
            {
                "name": "jobId exists",
                "input": 
                {
                        "jobId": 1
                }, 
                "expected": 'Fetching new images'
            },
            {
                "name": "not existing jobId",
                "input": 
                {
                        "jobId": 9999
                }, 
                "expected": 'jobId does not exist'
            }
        ]

        for case in testcases:
            payload = json.dumps(case["input"])
            headers = {'Content-Type': 'application/json'}
            self.conn.request("POST", "/getStatus", payload, headers)

            res = self.conn.getresponse()
            actual = res.read().decode("utf-8")
            self.assertIn(
                case["expected"],
                actual,
                "failed test {} expected {}, actual {}".format(
                    case["name"], case["expected"], actual
                ),
            )
            
if __name__ == '__main__':

    unittest.main()