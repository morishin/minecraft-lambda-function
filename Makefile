package:
	docker build . -t packager
	docker run --rm -it -v $(PWD):/app:rw packager
	zip minecraft_lambda_function.zip minecraft_lambda_function.py
	cd venv-for-deployment/lib/python2.7/site-packages && zip -r ../../../../minecraft_lambda_function.zip * .*
	echo "Completed. Please upload minecraft_lambda_function.zip to AWS Lambda"
