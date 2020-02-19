cp alexa.py venv/lib/python3.6/site-packages/alexa.py
cp lambda_function.py venv/lib/python3.6/site-packages/lambda_function.py
cd venv/lib/python3.6/site-packages/
zip -r9 lambda_function.zip *
mv lambda_function.zip ../../../../lambda_function.zip
cd ../../../../
