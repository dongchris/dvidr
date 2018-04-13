import boto
from boto.s3.key import Key


def readImagefromS3(imageFile):
    """
        This function will be using the pem file for AWS.
        It will access a public S3 bucket called dvidr with
        the specified image file. The output is a url link
        for the image that will be passed onto the Google
        Cloud Vision API for processing.
    """
    with open('dvidr.pem') as f:
        keys = f.read().split(',')

    s3 = boto.connect_s3(
        aws_access_key_id=keys[0],
        aws_secret_access_key=keys[1]
    )
    bucket = s3.get_bucket("dvidr", validate=False)

    k1 = Key(bucket)
    k1.key = imageFile

    url_name = k1.generate_url(259200)

    return url_name

if __name__ == '__main__':
    print(readImagefromS3("85c.jpg"))
