from io import StringIO
import tos

from ..config import settings


class OSSManager:
    def __init__(self):
        self.url = "https://doc.c2sagent.com/"
        self.oss_client = tos.TosClientV2(
            settings.TOS_ACCESS_KEY,
            settings.TOS_SECRET_KEY,
            "tos-cn-beijing.volces.com",
            "cn-beijing",
        )

    def upload_object(self, bucket_name, object_name, content):

        self.oss_client.put_object(bucket_name, object_name, content=content)
        return self.get_url(object_name)

    def get_url(self, object_name):
        return self.url + object_name
