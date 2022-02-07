from invenio_records_permissions import BasePermissionPolicy

from invenio_records_permissions.generators import AnyUser, SystemProcess

class OAIPMHServerPermissionPolicy(BasePermissionPolicy):
    can_read = [AnyUser(), SystemProcess()]
    can_create = [AnyUser(), SystemProcess()]
    can_delete = [AnyUser(), SystemProcess()]
    can_update = [AnyUser(), SystemProcess()]
    can_search = [AnyUser(), SystemProcess()]
