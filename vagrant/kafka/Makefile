
all: virtualenv init start configure apps
clean: stop destroy

virtualenv:
	bin/venv.sh

init:
	bin/init.sh

start:
	bin/start.sh

configure:
	bin/configure.sh

stop:
	bin/stop.sh

destroy:
	bin/destroy.sh

apps:
	bin/init_apps.sh

init_messages:
	app/init_messages/put.sh
