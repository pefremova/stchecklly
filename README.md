# Status checker
State transition testing helper

**Installation**
```
pip install git+https://github.com/pefremova/stchecklly.git 
```

Use config (<a href="/examples/">examples</a>), run as command.<br>

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
