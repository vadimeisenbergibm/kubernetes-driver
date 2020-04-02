from .object_states import ObjectStates
from .object_record import ObjectRecord
from .request_record import RequestRecord

class EntityGroupRecord:

    UID = 'uid'
    OBJECTS = 'objects'
    HELM_RELEASES = 'helm-releases'
    REQUESTS = 'requests'

    def __init__(self, uid, objects=None, helm_releases=None, requests=None):
        self.uid = uid
        self.objects = objects if objects is not None else []
        self.helm_releases = helm_releases if helm_releases is not None else []
        self.requests = requests if requests is not None else []

    def __str__(self):
        return f'{self.__class__.__name__}(uid: {self.uid}, objects: {self.objects}, helm_releases: {self.helm_releases}, requests: {self.requests})'

    def __repr__(self):
        return f'{self.__class__.__name__}(uid: {self.uid!r}, objects: {self.objects!r}, helm_releases: {self.helm_releases!r}, requests: {self.requests!r})'