# minecraft-lambda-function
AWS Lambda function for managing Minecraft server.

You can play Minecraft Multiplayer $0.03 / hour. (See [DigitalOcean Pricing](https://www.digitalocean.com/pricing/#droplet))

## Features
### create⚒
<img src="https://cloud.githubusercontent.com/assets/1413408/21756322/2dda13ea-d663-11e6-9c16-53fe50475df0.png" width="640" />

### upload🚀
<img src="https://cloud.githubusercontent.com/assets/1413408/21756340/7fe91df2-d663-11e6-9a93-c88b85ffa6a2.png" width="640" />

### destroy💥
<img src="https://cloud.githubusercontent.com/assets/1413408/21756324/2de341cc-d663-11e6-8b41-e28ffcf22af4.png" width="640" />

## Deploy
1. Run `make package` to create zip package file.

2. Upload to AWS Lambda manually.

3. Set environment variables.
  `MINECRAFT_LAMBDA_FUNCTION_TOKEN`, `DIGITALOCEAN_API_TOKEN`, `SLACK_INCOMING_WEBHOOK_URL`, `S3_BUCKET_NAME`

  <img src="https://cloud.githubusercontent.com/assets/1413408/21749197/1259c696-d5dd-11e6-82a8-c1d7d0150d26.png" width="640"/>

4. Configure test event and execute.

  <img width="640" alt="lambda settings 2" src="https://cloud.githubusercontent.com/assets/1413408/21757090/324e335c-d66d-11e6-84e6-8b5a071568ba.png">


5. Receive Slack notification.

  <img src="https://cloud.githubusercontent.com/assets/1413408/21758786/42691616-d682-11e6-871c-05fb9f57911c.png" width="480"/>

## Advanced Usage
Execute minecraft-lambda-function with Slack Slash Command.

<img src="https://cloud.githubusercontent.com/assets/1413408/21756755/aaf11ad6-d668-11e6-82e1-9513630b1083.png" width="640"/>

API Gateway settings example is here: https://gist.github.com/morishin/88042177ffdbbdb3349b0530a9de5d1f

## License
MIT
