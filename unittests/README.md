Please run unittests in the virtual environment 
(as relative paths were used for file creation and imports)

--in the root folder--

(venv) : python3 -m unittest unittests/TestWebserver.py

Please note that, because __init__.py is executed in 'app', the flask server is started,
so a CTRL + C is needed to return to the terminal after running the tests