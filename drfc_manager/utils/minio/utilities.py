from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject

from drfc_manager.types_built.hyperparameters import HyperParameters

import io
import os
from minio import Minio as MinioClient
from minio.error import MinioException
from orjson import dumps, OPT_INDENT_2

from drfc_manager.types_built.model_metadata import ModelMetadata
from drfc_manager.utils.minio.exceptions.file_upload_exception import FileUploadException

_bucket_name = os.getenv('BUCKET_NAME')
_custom_files_folder = os.getenv('CUSTOM_FILES_FOLDER_PATH')
_reward_function_path = os.getenv('REWARD_FUNCTION_PATH')


def upload_hyperparameters(
    minio_client: MinioClient,
    hyperparameters: HyperParameters
):
    """
    Uploads hyperparameters to an S3 bucket.

    Args:
        minio_client (MinioClient): The client of the minio api
        hyperparameters (HyperParameters): The hyperparameters to minio.

    Returns:
        bool: True if the minio was successful, False otherwise.
    """

    try:
        hyperparameters_serialized = dumps(hyperparameters, option=OPT_INDENT_2)
        object_size = len(hyperparameters_serialized)
        object_name = 'hyperparameters.json'

        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            io.BytesIO(hyperparameters_serialized),
            length=object_size,
            content_type="application/json"
        )

        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name} file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def upload_reward_function(
    minio_client: MinioClient,
    reward_function_buffer: io.BytesIO
):
    try:
        buffer_size = reward_function_buffer.getbuffer().nbytes
        object_name = 'reward_function.py'

        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            reward_function_buffer,
            length=buffer_size,
            content_type="text/plain"
        )

        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name}  file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def upload_metadata(
    minio_client: MinioClient,
    model_metadata: ModelMetadata
):
    """
    Uploads metadata to an S3 bucket.

    Args:
        minio_client (MinioClient): The client of the minio api
        model_metadata (Model Metadata): The metadata to minio.

    Returns:
        bool: True if the minio was successful, False otherwise.
    """

    try:
        model_metadata_serialized = dumps(model_metadata, option=OPT_INDENT_2)
        object_size = len(model_metadata_serialized)
        object_name = 'model_metadata.json'

        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            io.BytesIO(model_metadata_serialized),
            length=object_size,
            content_type="application/json"
        )

        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name}  file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def upload_local_data(minio_client: MinioClient, local_data_path: str, object_name):
    try:
        result = minio_client.fput_object(
            _bucket_name,
            object_name=object_name,
            file_path=local_data_path,
        )

        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name}  file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def check_if_object_exists(minio_client: MinioClient, object_name: str):
    try:
        minio_client.stat_object(_bucket_name, object_name)
        return True
    except Exception:
        return False


def copy_object(minio_client: MinioClient, source_object_name: str, dest_object_name: str):
    try:
        minio_client.copy_object(
            _bucket_name,
            dest_object_name,
            CopySource(_bucket_name, source_object_name)
        )
        return True
    except MinioException:
        raise FileUploadException(message=f'Error copying {source_object_name} to {dest_object_name}')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def remove_objects_folder(minio_client: MinioClient, object_name: str):
    try:
        objects = minio_client.list_objects(_bucket_name, prefix=object_name)
        objects_names = [object.object_name for object in objects]
        delete_objects = [DeleteObject(object_name) for object_name in objects_names]

        minio_client.remove_objects(
            _bucket_name,
            delete_objects,
        )
        return True
    except MinioException:
        raise FileUploadException(message=f'Error deleting {object_name} folder')
    except Exception as e:
        raise FileUploadException(original_exception=e)
