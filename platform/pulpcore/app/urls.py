"""pulp URL Configuration"""

import collections
import re
import warnings

from django.core.exceptions import AppRegistryNotReady
from django.conf.urls import url, include
from rest_framework_nested import routers

from pulpcore.app.apps import pulp_plugin_configs
from pulpcore.app.views import ContentView, StatusView
import logging
log = logging.getLogger(__name__)

root_router = routers.DefaultRouter(
    schema_title='Pulp API',
    schema_url='/api/v3'
)  #: The Pulp Platform v3 API router, which can be used to manually register ViewSets with the API.

#
all_routers = [root_router]
# registered_viewsets = []
#
# def get_parent_viewsets(viewset):
#     return [vs for vs in registered_viewsets if issubclass(vs, viewset.parent_viewset)]
#
# def routers_for_nested_viewset(viewset):
#     """
#     Find the router for a nested viewset.
#
#     Args:
#         viewset (pulpcore.app.viewsets.NamedModelViewSet): a viewset for which a nested router
#             should exist
#
#     Returns:
#         routers.NestedDefaultRouter: the nested router whose parent_prefix corresponds to the
#             viewset's nest_prefix attribute.
#
#     Raises:
#         LookupError: if no nested router is found for the viewset.
#
#     """
#     if not viewset.nest_prefix:
#         return [root_router]
#     else:
#         #######
#         if viewset.parent_viewset.is_master_viewset():
#             extra_regex = "\/.+$"
#         else:
#             extra_regex = ""
#
#         regex = re.compile("^{prefix}{detail_type}".format(prefix=viewset.nest_prefix, detail_type=extra_regex))
#         #######
#         register_with = []
#         for router_candidate in all_routers:
#             if hasattr(router_candidate, 'parent_prefix') and re.search(regex, router_candidate.parent_prefix):
#                 register_with.append(router_candidate)
#         # routers = [r for r in nested_routers if re.search(regex, r.parent_prefix)]
#         # router_prefixes = [router.parent_prefix for router in nested_routers]
#         # routers_to_register_with = filter(regex.match, router_prefixes)
#        return register_with
#
#  """
#  The problem with this approach is that parent viewsets don't know they have children,
#  so I can't determine whether I need to create a new router or not. If I make a tree instead of 
#  and ordered list, then at registration time, a vs knows it will need to make a new router,
#  and the children will already know which router to use. This could be problematic with master/detail routers though.
#
#  """
# viewsets_by_depth = collections.defaultdict(list)
# for app_config in pulp_plugin_configs():
#     for viewset in app_config.named_viewsets.values():
#         if not viewset.is_master_viewset():
#             viewsets_by_depth[viewset._get_nest_depth()].append(viewset)
#
# for depth in sorted(viewsets_by_depth.keys()):
#     for viewset in viewsets_by_depth[depth]:
#         # TODO(asmacdo)consolidate
#         register_with = routers_for_nested_viewset(viewset)
#         for router in register_with:
#             router.register(viewset.urlpattern(), viewset, viewset.view_name())
#         # if hasattr(viewset, 'router_lookup'):
#         # 
#         registered_viewsets.append(viewset)
#         if not register_with:
#             parent_viewsets = get_parent_viewsets(viewset)
#             for pvs in parent_viewsets:
#                 #### UGHGHHH I DONT KNOW WHICH FREAKING ROUTER TO REGISTER THE NEW ROUTER WITHHHHHHHHHHHHHHHHB
#                 new_router = routers.NestedDefaultRouter(router, pvs.urlpattern(), lookup=pvs.router_lookup)
#                 all_routers.append(new_router)
#                 register_with.append(new_router)
#  
#
class VSNode(object):
    def __init__(self, viewset=None):
        #self = viewset?
        self.vs = viewset
        self.children = []

    def get_parent_node(self, viewset):
        if not viewset.parent_viewset:
            return self
        if self.vs and issubclass(self.vs, viewset.parent_viewset):
            return self
        for child in self.children:
            node = child.get_parent_node(viewset)
            if node:
                return node

    def add(self, viewset):
        node = self.get_parent_node(viewset)
        node.children.append(VSNode(viewset))

    def __repr__(self):
        if not self.vs:
            return "Root"
        else:
            return str(self.vs)
    
def build_tree(viewsets):
    vs_tree = VSNode()
    sorted_by_depth = sorted(all_viewsets, key=lambda vs: vs._get_nest_depth())
    for vs in sorted_by_depth:
        vs_tree.add(vs)
    return vs_tree


def register_vs_tree(node, router):
    # If not root
    if node.vs:
        router.register(node.vs.urlpattern(), node.vs, node.vs.view_name())

        if node.children:
            router = routers.NestedDefaultRouter(router, node.vs.urlpattern(), lookup=node.vs.router_lookup)
            all_routers.append(router)

    # Always
    for child in node.children:
        register_vs_tree(child, router)

all_viewsets = []
for app_config in pulp_plugin_configs():
    for viewset in app_config.named_viewsets.values():
        all_viewsets.append(viewset)
 
vs_tree = build_tree(all_viewsets)
register_vs_tree(vs_tree, root_router)

#

# for depth in sorted(viewsets_by_depth.keys()):
#     for viewset in viewsets_by_depth[depth]:
#         # TODO(asmacdo)consolidate
#         register_with = routers_for_nested_viewset(viewset)
#         for router in register_with:
#             router.register(viewset.urlpattern(), viewset, viewset.view_name())
#         # if hasattr(viewset, 'router_lookup'):
#         # 
#         registered_viewsets.append(viewset)
#         if not register_with:
#             parent_viewsets = get_parent_viewsets(viewset)
#             for pvs in parent_viewsets:
#                 #### UGHGHHH I DONT KNOW WHICH FREAKING ROUTER TO REGISTER THE NEW ROUTER WITHHHHHHHHHHHHHHHHB
#                 new_router = routers.NestedDefaultRouter(router, pvs.urlpattern(), lookup=pvs.router_lookup)
#                 all_routers.append(new_router)
#                 register_with.append(new_router)
#

urlpatterns = [
    url(r'^{}/'.format(ContentView.BASE_PATH), ContentView.as_view()),
    url(r'^api/v3/status/', StatusView.as_view()),
]

for each in all_routers:
    urlpatterns.append(url(r'^api/v3/', include(each.urls)))
