import yaml
import re
from kubedriver.kubeobjects.object_config import ObjectConfiguration
from kubedriver.kubeobjects import namehelper
from .records import GroupRecord, ObjectRecord, RequestRecord

class ConfigMapStorageFormat:

    def dump_group_record(self, group_record):
        dump = {
            GroupRecord.UID: group_record.uid,
            GroupRecord.OBJECTS: self.dump_object_records(group_record.objects),
            GroupRecord.REQUESTS: self.dump_request_records(group_record.requests)
        }
        return dump

    def load_group_record(self, data):
        uid = data.get(GroupRecord.UID)
        raw_objects = data.get(GroupRecord.OBJECTS, [])
        objects = self.load_object_records(raw_objects)
        raw_requests = data.get(GroupRecord.REQUESTS)
        requests = self.load_request_records(raw_requests)
        return GroupRecord(uid, objects, requests)

    def dump_request_record(self, request_record):
        dump = {
            RequestRecord.UID: request_record.uid,
            RequestRecord.OPERATION: request_record.operation,
            RequestRecord.STATE: request_record.state,
            RequestRecord.ERROR: request_record.error
        }
        return dump

    def load_request_record(self, data):
        uid = data.get(RequestRecord.UID)
        operation = data.get(RequestRecord.OPERATION)
        state = data.get(RequestRecord.STATE)
        error = data.get(RequestRecord.ERROR, None)
        return RequestRecord(uid, operation, state=state, error=error)

    def dump_request_records(self, request_records):
        pre_dump = []
        for request in request_records:
            pre_dump.append(self.dump_request_record(request))
        return yaml.safe_dump(pre_dump)

    def load_request_records(self, data):
        raw_records = yaml.safe_load(data)
        records = []
        for raw_record in raw_records:
            records.append(self.load_request_record(raw_record))
        return records
    
    def dump_object_record(self, object_record):
        dump = {
            ObjectRecord.CONFIG: object_record.config,
            ObjectRecord.STATE: object_record.state,
            ObjectRecord.ERROR: object_record.error
        }
        return dump

    def load_object_record(self, data):
        config = data.get(ObjectRecord.CONFIG)
        state = data.get(ObjectRecord.STATE)
        error = data.get(ObjectRecord.ERROR, None)
        return ObjectRecord(config, state=state, error=error)

    def dump_object_records(self, object_records):
        pre_dump = []
        for record in object_records:
            pre_dump.append(self.dump_object_record(record))
        return yaml.safe_dump(pre_dump)
    
    def load_object_records(self, data):
        raw_objs = yaml.safe_load(data)
        objects = []
        for raw_obj in raw_objs:
            objects.append(self.load_object_record(raw_obj))
        return objects

class ConfigMapRecordPersistence:

    def __init__(self, kube_api_ctl, storage_namespace, cm_api_version='v1', cm_kind='ConfigMap', cm_data_field='data'):
        self.kube_api_ctl = kube_api_ctl
        self.storage_namespace = storage_namespace
        self.cm_api_version = cm_api_version
        self.cm_kind = cm_kind
        self.cm_data_field = cm_data_field
        self.format = ConfigMapStorageFormat()

    def create(self, group_record):
        cm_config = self.__build_config_map_for_record(group_record)
        self.kube_api_ctl.create_object(cm_config, default_namespace=self.storage_namespace)

    def update(self, group_record):
        cm_config = self.__build_config_map_for_record(group_record)
        self.kube_api_ctl.update_object(cm_config, default_namespace=self.storage_namespace)

    def get(self, group_uid):
        cm_name = self.__determine_config_map_name(group_uid)
        record_cm = self.kube_api_ctl.read_object(self.cm_api_version, self.cm_kind, cm_name, namespace=self.storage_namespace)
        return self.__read_config_map_to_record(record_cm)

    def delete(self, group_uid):
        cm_name = self.__determine_config_map_name(group_uid)
        self.kube_api_ctl.delete_object(self.cm_api_version, self.cm_kind, cm_name, namespace=self.storage_namespace)

    def __determine_config_map_name(self, group_uid):
        potential_name = 'kdr-{0}'.format(group_uid)
        return namehelper.safe_subdomain_name(potential_name)

    def __build_config_map_for_record(self, group_record):
        cm_name = self.__determine_config_map_name(group_record.uid)
        cm_obj_config = {
            ObjectConfiguration.API_VERSION: self.cm_api_version,
            ObjectConfiguration.KIND: self.cm_kind,
            ObjectConfiguration.METADATA: {
                ObjectConfiguration.NAME: cm_name,
                ObjectConfiguration.NAMESPACE: self.storage_namespace
            },
            self.cm_data_field: self.format.dump_group_record(group_record)
        }
        return ObjectConfiguration(cm_obj_config)

    def __read_config_map_to_record(self, config_map):
        cm_data = config_map.data
        group_record = self.format.load_group_record(cm_data)
        return group_record