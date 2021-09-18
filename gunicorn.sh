# kill -9 `ps axu|grep guni|awk -F" " {'print $2'}`
source venv/bin/activate
#gunicorn -w 12 --timeout 180 -b 192.168.1.68:4200 ahoy:app --reload --log-level INFO
gunicorn -w 12 --timeout 180 -b 0:4444 ahoy:app --reload --log-level INFO
