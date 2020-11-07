# mergerepospython
RESTful API to merge an owner's public (excluding forks) github and bitbucket repos together

## Install:

python 3.7.4

pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

### Spin up the service

```
# start up local server
python3 gitinfo.py
```

### Making Requests

```
curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/repos -d '{"github":"https://github.com/{owner}","bitbucket":"https://bitbucket.org/{owner}"}'

Rest Client:
http://127.0.0.1/5000/repos

{
	"github":"https://github.com/{owner}",
	"bitbucket":"https://bitbucket.org/{owner}"
	
}

replace {owner}
```


## What'd I'd like to improve on...

```
I'd like to improve on making the checking the strings sent in the json to verify it is the correct format and add unit testing
```

