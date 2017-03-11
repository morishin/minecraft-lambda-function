import os
import time

import boto3
import digitalocean
import paramiko
import requests
from Crypto.PublicKey import RSA
from retry import retry

DIGITALOCEAN_API_TOKEN = os.getenv("DIGITALOCEAN_API_TOKEN")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SLACK_INCOMING_WEBHOOK_URL = os.getenv("SLACK_INCOMING_WEBHOOK_URL")
MINECRAFT_LAMBDA_FUNCTION_TOKEN = os.getenv("MINECRAFT_LAMBDA_FUNCTION_TOKEN")


def lambda_handler(event, context):
    if event["token"] != MINECRAFT_LAMBDA_FUNCTION_TOKEN:
        return {"message": ":no_good: Invalid token. Your request body is: " + str(event)}

    try:
        action = event["text"]
        if action == "create":
            _slack_notify(":muscle: Creating server...")
            message = create_server()
            _slack_notify(message)
        elif action == "upload":
            _slack_notify(":muscle: Uploading world data...")
            message = upload_world()
            _slack_notify(message)
        elif action == "destroy":
            # upload
            _slack_notify(":muscle: Uploading world data...")
            message = upload_world()
            _slack_notify(message)

            _slack_notify(":muscle: Destroying server...")
            message = destroy_server()
            _slack_notify(message)
        else:
            message = "Invalid action: " + action
            _slack_notify(message)
    except Exception as e:
        message = ":no_good: Error: " + e.message
        _slack_notify(message)

    return {"message": message}


def create_server():
    private_key = _get_ssh_private_key()
    public_key = "ssh-rsa " + private_key.get_base64()
    droplet = _create_droplet(public_key)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    _ssh_connect(client, hostname=droplet.ip_address, username="root", pkey=private_key)

    bucket_location = boto3.client("s3").get_bucket_location(Bucket=S3_BUCKET_NAME)["LocationConstraint"]
    world_path = "https://s3-%s.amazonaws.com/%s/world.zip" % (bucket_location, S3_BUCKET_NAME)

    commands = [
        "docker run -d -e EULA=TRUE -e WORLD=%s -e SLACK_WEBHOOK_URL=%s --name minecraft -p 25565:25565 morishin127/minecraft-server" % (world_path, SLACK_INCOMING_WEBHOOK_URL)
    ]
    _exec_commands(client, commands)

    message = ":hammer_and_pick: instance created. IP: `" + droplet.ip_address + "`"
    return message


def upload_world():
    manager = digitalocean.Manager(token=DIGITALOCEAN_API_TOKEN)
    all_droplets = manager.get_all_droplets()
    droplet = filter(lambda droplet: droplet.name == "minecraft", all_droplets)[0]

    private_key = _get_ssh_private_key()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    _ssh_connect(client, hostname=droplet.ip_address, username="root", pkey=private_key)

    commands = [
        "cd /root",
        "docker cp minecraft:/data/world ./",
        "apt install -y zip",
        "zip -r world.zip world"
    ]
    _exec_commands(client, commands)

    sftp = client.open_sftp()
    sftp.get("/root/world.zip", "/tmp/world.zip")

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(S3_BUCKET_NAME)
    obj = bucket.Object("world.zip")
    obj.put(Body=open("/tmp/world.zip", "rb"))
    obj.Acl().put(ACL="public-read")

    bucket_location = boto3.client("s3").get_bucket_location(Bucket=S3_BUCKET_NAME)["LocationConstraint"]
    world_path = "https://s3-%s.amazonaws.com/%s/world.zip" % (bucket_location, S3_BUCKET_NAME)

    message = ":rocket: Uploaded world.zip: " + world_path
    return message


def destroy_server():
    manager = digitalocean.Manager(token=DIGITALOCEAN_API_TOKEN)
    all_droplets = manager.get_all_droplets()
    droplet = filter(lambda droplet: droplet.name == "minecraft", all_droplets)[0]
    ip_address = droplet.ip_address
    droplet.destroy()

    message = ":boom: instance destroyed. IP: `" + ip_address + "`"
    return message


@retry(tries=4, delay=5)
def _ssh_connect(client, hostname, username, pkey):
    print "Trying SSH connection..."
    client.connect(hostname=hostname, username=username, pkey=pkey)


def _exec_commands(client, commands):
    for command in commands:
        print "Executing {}".format(command)
        stdin, stdout, stderr = client.exec_command(command)
        print stdout.read()
        print stderr.read()


def _create_droplet(public_key):
    key_name = 'minecraft-lambda-function-' + public_key[-7:]
    manager = digitalocean.Manager(token=DIGITALOCEAN_API_TOKEN)
    keys = manager.get_all_sshkeys()
    if len(filter(lambda k: k.name == key_name, keys)) == 0:
        key = digitalocean.SSHKey(token=DIGITALOCEAN_API_TOKEN,
                                  name=key_name,
                                  public_key=public_key)
        key.create()
        keys.append(key)

    droplet = digitalocean.Droplet(token=DIGITALOCEAN_API_TOKEN,
                                   name="minecraft",
                                   region="sgp1",
                                   image="docker-16-04",
                                   size_slug="2gb",
                                   ssh_keys=keys,
                                   backups=False)
    droplet.create()

    manager = digitalocean.Manager(token=DIGITALOCEAN_API_TOKEN)
    created_droplet = manager.get_droplet(droplet.id)
    return created_droplet


def _get_ssh_private_key():
    key_file_name = "id_rsa"
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(S3_BUCKET_NAME)
    obj = bucket.Object(key_file_name)
    try:
        obj.load()
    except:
        _generate_ssh_key(key_file_name)

    client = boto3.client("s3")
    client.download_file(S3_BUCKET_NAME, key_file_name, "/tmp/" + key_file_name)
    private_key = paramiko.RSAKey.from_private_key_file("/tmp/" + key_file_name)
    return private_key


def _generate_ssh_key(key_file_name):
    key = RSA.generate(2048)
    key_file_path = "/tmp/" + key_file_name
    with open(key_file_path, "w") as content_file:
        os.chmod(key_file_path, 0600)
        content_file.write(key.exportKey("PEM"))
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(S3_BUCKET_NAME)
    obj = bucket.Object(key_file_name)
    obj.put(Body=open(key_file_path, "rb"))


def _slack_notify(message):
    requests.post(SLACK_INCOMING_WEBHOOK_URL, {"payload": '{"text": "%s"}' % (message)})
