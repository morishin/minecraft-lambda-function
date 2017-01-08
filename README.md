# minecraft-lambda-function
AWS Lambda function for managing Minecraft server.

Lambda event is the following structure.
```json
{
  "token": "<MINECRAFT_LAMBDA_FUNCTION_TOKEN>",
  "text": "[create|upload|destroy]"
}
```

## Features
### create
![create](https://cloud.githubusercontent.com/assets/1413408/21748634/e4483e1e-d5cc-11e6-85fb-e1b1f174fbb3.png)
### upload
![upload](https://cloud.githubusercontent.com/assets/1413408/21748635/e448a00c-d5cc-11e6-86c2-be688f00f597.png)
### destroy
![destroy](https://cloud.githubusercontent.com/assets/1413408/21748633/e447f378-d5cc-11e6-8bd6-d1c234e70e70.png)

## Deploy
Run `make package` to create zip package file and upload to AWS Lambda manually.

## License
MIT
