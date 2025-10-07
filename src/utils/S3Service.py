#version 2.2
from datetime import datetime
import logging
import os
import sys
import threading
import boto3
from botocore.client import ClientError
from contextlib import suppress
from src.config.config import Configurations


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()


def upload_file(file_name: str, object_name="", folder="", addDateToName=False,
                bucket_name=Configurations.LAMBDA_VC_BUCKET_NAME) -> bool:
    if not object_name:
        object_name = os.path.basename(file_name)

    if addDateToName:
        object_name = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-") + object_name

    if folder and folder[-1] != '/':
        folder += '/'
    if folder and folder[0] == '/':
        folder = folder[1:]
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(
            file_name, bucket_name, folder + object_name,
            Callback=ProgressPercentage(file_name)
        )
    except ClientError as e:
        logging.error(e)
        return False
    except Exception as e:
        print("ERROR->", e.__str__())
        return False
    return True


def deleteFile(file):
    if not os.path.exists(file):
        return

    if os.path.isfile(file):
        os.remove(file)
        return

    for root, dirs, files in os.walk(file, topdown=False):
        for f in files:
            file_path = os.path.join(root, f)
            os.remove(file_path)
        for d in dirs:
            dir_path = os.path.join(root, d)
            os.rmdir(dir_path)

    os.rmdir(file)


def download_file_bucket(bucket_name: str, bucket_file_name: str, local_file_name=None):
    if local_file_name is None:
        local_file_name = bucket_file_name
    try:
        s3 = boto3.client('s3')
        auxFolder = os.path.dirname(local_file_name)
        if auxFolder != "" and not os.path.exists(auxFolder):
            os.makedirs(auxFolder, exist_ok=True)
        with open(local_file_name, 'wb') as f:
            s3.download_fileobj(bucket_name, bucket_file_name, f)
    except ClientError as e:
        with suppress(Exception):
            deleteFile(local_file_name)
            print("ERROR-*->", e.__str__())
            logging.error(e)
        return False
    except Exception as e:
        with suppress(Exception):
            deleteFile(local_file_name)
            print("ERROR->", e.__str__())
            logging.error(e)
        return False
    return True


def download_file(bucket_file_name: str, local_file_name=None):
    return download_file_bucket(Configurations.LAMBDA_VC_BUCKET_NAME, bucket_file_name, local_file_name)


def list_files(prefix: str, bucket_name: str):
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket_name)
    auxP = prefix + "" if prefix.endswith("/") else "/"
    out = []
    for my_bucket_object in my_bucket.objects.filter(Prefix=prefix):
        if my_bucket_object.key == auxP:  # ignore root folder
            continue
        out.append(my_bucket_object.key)
    return out


def download_files_list(prefix: str, local_folder_name=None) -> bool:
    res = True
    for my_bucket_object in list_files(prefix, Configurations.LAMBDA_VC_BUCKET_NAME):
        if not isinstance(local_folder_name, str):
            download_file(my_bucket_object.key)
        else:
            local_file_path = os.path.join(local_folder_name, my_bucket_object.key)
            if not os.path.exists(os.path.dirname(local_file_path)):
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            res = res and download_file(my_bucket_object.key, local_file_path)
    return res


def delete_file(key, bucketName=Configurations.LAMBDA_VC_BUCKET_NAME):
    s3 = boto3.resource('s3')
    s3.Object(bucketName, key).delete()