# automated-assignment-evaluation
Final Year Project for automated assignment evaluation

## Setup

* Clone the repo
* Create your branch and move to it `git checkout -b branch_name`
* Activate your venv using `source /path/to/venv/bin/activate`
* ``pip install -r requirements.txt``
* Intall redis `sudo apt-get install redis-server`
* First time on cloning, run `pre-commit install`

## Git Pre Commit Hooks

* When you commit, `black` will be used to format the code
* After that `flake8` will be used to test the code style
* If `black` says failed then it means that black had to make changes to the code to format it correctly.
* If `black` fails and `flake8` passes, then just commit again, it should work.
* Normally `black` should just ensure `flake8` never fails.

* Both `black` and `flake` only run on the code that has been changed in the commit


## Running the project

* Run `makemigrations` `migrate` and `runserver` with `manage.py`
* For celery, run `celery -A evalmgr worker -l info`


## Running on docker

* In the `settings.py` uncomment the redis conf lines
* Run `docker-compose up` 
* May have issues with the db read/write.


* ### Whenever a feature is completed, merge your branch against with the `master` branch and resolve any conflicts and only then create a pull request from your branch to the `master` branch

* While creating the pull request, add others as reviewers and reference it in the issue it is fixing
