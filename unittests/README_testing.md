Please run unittests in the virtual environment
(as relative paths were used for file creation and imports).

### In the root folder:

```bash
(venv) : python3 -m unittest unittests/TestWebserver.py
```
- Note that, because __init__.py is executed in the app directory, the Flask server is
started, so a CTRL + C is needed to return to the terminal after running the tests.