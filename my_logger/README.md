# Custom Logger Library
This library provides a customizable logger with support for additional attributes, stream and file logging, as well as integration with Azure Application Insights.

## Features
1. Custom Attributes: You can add any number of custom attributes to log records.
2. Stream and File Logging: The Logger class allows you to enable or disable stream and file handlers for logging.
3. Azure Application Insights Integration: By providing an Azure connection string, you can enable logging to Azure App Insights.

## Usage

You can create a logger object with optional parameters for stream handling, file handling, log levels, and custom dimensions:

```python
from custom_logger import Logger

logger = Logger(username="Tester", OS="Windows", local="local", custom_dimensions={'job_id': 2020}, file_handler=True)
logger.get_logger()
logging.info("Testing!")

# [2023-08-22 18:28:10] - [INFO] - [Tester] - [Windows] - [local] - [{'job_id': 2020}] - (main.py).<module>(10) - Testing!
```

It can affect all the log messages generated within imported modules:

```python
from custom_logger import Logger
from helper import do

logger = Logger(username="Tester", OS="Windows", local="local", custom_dimensions={'job_id': 2020}, file_handler=True)
logger.get_logger()
do()

# [2023-08-22 18:30:59] - [INFO] - [Tester] - [Windows] - [local] - [{'job_id': 2020}] - (helper.py).do(7) - HELLO
```

### Installation

Create the wheel file:
```bash
python setup.py sdist bdist_wheel
```

To install this library, run:
```bash
pip install <path-to-whl-file>
```

## Dependencies
This library uses AzureLogHandler from OpenCensus for Azure Application Insights integration:
* `opencensus`
* `opencensus-context`
* `opencensus-ext-azure`