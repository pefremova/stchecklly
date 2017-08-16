# Status checker
State transition testing helper<br>
Use config (<a href="/example/">examples</a>), run as command or run as django-command.<br>


**Installation**
```
pip install git+https://github.com/pefremova/stchecklly.git 
```

For Django:<br>
add 'stchecklly' to INSTALLED_APPS for use as django-command (by manage.py state_checker)


**Features**
* generate list of available transitions with given length
* show diagram (use <a href="http://www.graphviz.org/">graphviz</a>)


**Output example**
```
state_checker -c config.py -v 2
[create, approve]
********************
start state: None
create (next state: created)
approve (next state: approve)
********************
[create, delete]
********************
start state: None
create (next state: created)
delete (next state: deleted)
********************
```
