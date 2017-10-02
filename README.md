TubeSpam
========

## Installing

This app currently uses Python 2. Use of virtualenv is recommended:

1. Install virtualenv:
```
pip install virtualenv
```

2. Create virtual environment:
```
virtualenv --python=python2 venv
```

3. Activate the virtual environment (you're going to need this to every terminal):
```
source venv/bin/activate
```

4. Install app libraries:
```
pip install -r requirements.txt
```

5. Configure the following environment variables (this is the toughest part, but you should have them saved somewhere):
```
TS_SECRET_KEY
TS_DATABASE_URL
TS_SENDGRID_USR
TS_SENDGRID_PWD
TS_ADMIN_MAIL
TS_YOUTUBE_API_KEY
TS_NEW_RELIC_CONFIG_FILE
TS_NEW_RELIC_ENVIRONMENT
```

6. Apply migrations:
```
python manage.py migrate
```

7. Fit default classifier to be used as a fallback:
```
python manage.py fitdefaultclassifier
```

## Testing

1. Activate the virtual environment if you have not done yet:
```
source venv/bin/activate
```

2. Run the tests:
```
python manage.py test app
```

## Running

1. Activate the virtual environment if you have not done yet:
```
source venv/bin/activate
```

2. Run the application:
```
python manage.py runserver
```
