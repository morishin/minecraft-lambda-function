package:
	docker build . -t packager
	docker run --rm -it -v $(PWD):/app:rw packager
	zip minecraft_lambda_functions.zip minecraft_lambda_functions.py
	cd venv/lib/python2.7/site-packages && zip -r ../../../../minecraft_lambda_functions.zip * .*
	echo "Completed. Please upload minecraft_lambda_functions.zip to AWS Lambda"
