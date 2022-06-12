
## About AWS RSS Feed Parser
This solution can be used to deploy a Lambda function that will parse content from an AWS RSS Feed and save entries to an S3 bucket. By default, Lambda will check the feed every midnight, and if new entries are found, they will be saved to S3 in a tabular form.

## Create lambda layer
```
$ cd build/
$ bash create_new_layer.sh config
```
## Configure context parameters
Update `cdk.json` as following:
* Copy lambda layer arn and update layer_version_arn' parameter in the `cdk.json` file.
* Provide a human-readable bucket name.
* Specify your email address to receive notifications.

## Install dependencies
```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Deploy
At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
$ cdk deploy
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!


## Usage
Lambda will be triggered daily by EventBridge Scheduled Rule at 00:02 UTC time.
You will receive an email with the execution status and the link to a file on S3 bucket.



