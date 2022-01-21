Like [civic_calendar](https://github.com/registerguard/civic_calendar) only BETTER.

### If you'd like it to serve Presto-formatted HTML  ###

Request a GET argument of `html` set to anything, i.e.,  

` ... /civic/print/?html=foo`

... and you'll get Presto-ready HTML. Just flip your editor to `Source` and paste it in.

### Hot AWS-hosted Django development server tip ###

Use `0.0.0.0:8080` or ... 

Use the AWS Internal IP address (check the AWS Console to find out what it is) and the runserver'll work (provided the port you use is open). i.e.:

```shell
$ python manage.py runserver 172.16.1.174:8080 --settings=django_root.settings.staging
```

Hat tip: https://stackoverflow.com/questions/9323076/ec2-hosts-django-with-ip-address-cant-be-assigned-to-error#answer-9323154

Also, remember to use a `settings` that has `Debug = True` so you can get your assets served by the test server.
