
To run without Pycharm running, navigate to pycharm root directory to activate venv.  Run command:

You will need your own api key from OpenAI.  Place that key in .env file in root of directory.  Inside that file you put: OPENAI_API_KEY=yourkeygoeshere

My chats.json file is not in the repo.  Upon running this app in pycharm a chats.json file will be created tracking all input/output.

Make sure your .env file and chats.json files are not being committed - the .gitignore file should be intact with repo and prevent this.