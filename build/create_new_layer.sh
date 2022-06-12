#!/bin/bash
set -e # Exit immediately if a pipeline returns a non-zero status

if [ -z "$1" ]
then
    echo "Config file is required. Exiting..."
    exit 1
fi

source "$1"

check_package () {
    echo -n "Checking if necessary system packages is installed... "
    python --version > /dev/null
    pip --version > /dev/null
    aws --version > /dev/null
    jq --version > /dev/null
    echo "Success!"
}
check_package

# BUCKET_NAME="shuraosipov-content"
# PYTHON_VERSION="python3.9"
# LAYER_NAME="$1"
LAYER_PATH="python/lib/${PYTHON_VERSION}/site-packages/"
PACKAGE_NAME="${LAYER_NAME}-lambda-layer.zip"
OUTPUT_FOLDER="$(mktemp -d)"

echo "Python version - ${PYTHON_VERSION}"
echo "Package name - ${PACKAGE_NAME}"
echo "Building lambda layer in ${OUTPUT_FOLDER}/${LAYER_PATH} folder"
echo "S3 bucket for storing lambda layer package - ${BUCKET_NAME}"
cp requirements.txt $OUTPUT_FOLDER
cd $OUTPUT_FOLDER

echo -n "Installing dependencies...  "
pip install -r requirements.txt -t ${LAYER_PATH} > /dev/null 2>&1 
echo "Success!"

echo -n "Compiling the .zip file... "
zip -q -r9 ${PACKAGE_NAME} . && echo "Success!"
SIZE=$(du -sh ${PACKAGE_NAME} | cut -f1)
echo "Archive size is ${SIZE}"

echo -n "Uploading lambda layer package to S3... "
aws s3 cp ${PACKAGE_NAME} s3://${BUCKET_NAME} > /dev/null 2>&1 
echo "Success!"

echo -n "Publishing a layer...  "
response=$(aws lambda publish-layer-version \
    --layer-name ${LAYER_NAME} \
    --description "${LAYER_DESCRIPTION}" \
    --content S3Bucket=${BUCKET_NAME},S3Key=${PACKAGE_NAME} \
    --compatible-runtimes ${PYTHON_VERSION})
echo "Success!"

echo -n "Cleaning up... "
rm -rf ${OUTPUT_FOLDER} && echo "Success!"

echo -n "Enjoy your newly created layer - "
echo $response | jq -r '.LayerVersionArn'