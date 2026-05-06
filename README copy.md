# GSP_API
Graphic Server Protocol Application User Interface


## Installation

Create a virtual environment and install the required packages:

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install required packages
pip install -e . 
```

---

## FAQ
### Q. How to remove datoviz log ?
A. You can set the log level of datoviz with ```DVZ_LOG_LEVEL``` environment variable. See the [doc](https://datoviz.org/discussions/CONTRIBUTING/#console-logging)

```
DVZ_LOG_LEVEL=4 GSP_RENDERER=datoviz python your_script.py
```