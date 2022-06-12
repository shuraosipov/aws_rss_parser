# Create a new Lambda Layer

## Create an S3 bucket for storing lambda layers
By default Lambda deployment package size is limited to 50MB.
To overcome this limitation we will store lambda layer packages on S3 bucket.

Use an existing bucket or create a new one using the command below:
```
aws s3 mb s3://shuraosipov-lambda-layers
```

## Update requirements.txt
Specify a list of packages you want to include to a layer in `requirements.txt` file.
 
Default content is:
```
feedparser
```

## Configure layer parameters
Provide python version, layer name, layer description and target S3 backet for storing layers in the `confg` file.

Default content is:
```
PYTHON_VERSION="python3.9"
LAYER_NAME="feedparser"
LAYER_DESCRIPTION="Layer containing feedparser library"
BUCKET_NAME="shuraosipov-lambda-layers"
```

## Create a layer
From the app root folder:
```
$ bash create_new_layer.sh config
```

You will see the following output:
```
Checking if necessary system packages is installed... Success!
Python version - python3.9
Package name - feedparser-lambda-layer.zip
Building lambda layer in /tmp/tmp.nqoEObnXYl/python/lib/python3.9/site-packages/ folder
S3 bucket for storing lambda layer package - shuraosipov-lambda-layers
Installing dependencies...  Success!
Compiling the .zip file... Success!
Archive size is 45M
Uploading lambda layer package to S3... Success!
Publishing a layer...  Success!
Cleaning up... Success!
Enjoy your newly created layer - arn:aws:lambda:us-east-1:************:layer:feedparser:1
```