AHOY_PORT=4444
AHOY_HOST=192.168.1.68


###################################################

export AHOY_PORT=$AHOY_PORT
export AHOY_HOST=$AHOY_HOST


echo $AHOY_HOST $AHOY_PORT


source venv/bin/activate

gunicorn -w 12 --timeout 180 -b $AHOY_HOST:$AHOY_PORT ahoy:app --reload --log-level INFO
