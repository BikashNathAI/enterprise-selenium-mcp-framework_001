.PHONY: test smoke regression api bdd data report clean all

smoke:
	pytest tests/ -m smoke -v

regression:
	pytest tests/ -m regression -v

ui:
	pytest tests/ui/ -v

api:
	pytest tests/api/ -v

bdd:
	pytest tests/ui/test_bdd_google.py -v

data:
	pytest tests/ui/test_data_driven.py -v

all:
	pytest tests/ -v

report:
	pytest tests/ -v --html=reports/test-report.html --self-contained-html

parallel:
	pytest tests/ -n auto -v

clean:
	rmdir /s /q reports\allure-results 2>nul
	rmdir /s /q screenshots 2>nul
	mkdir reports\allure-results
	mkdir screenshots
	echo Cleaned!