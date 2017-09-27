Like [civic_calendar](https://github.com/registerguard/civic_calendar) only BETTER.

#### Hot AWS-hosted Django development server tip ####
Use the AWS Internal IP address and the runserver'll work (provided the port you use is open). i.e.:

```shell
$ python manage.py runserver 172.16.1.174:8080 --settings=django_root.settings.staging
```

Also, remember to use a setting that has `Debug = True` so you can get your assets served by the test server.
