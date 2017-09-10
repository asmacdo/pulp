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
all_routers = [root_router]

class VSNode(object):
    def __init__(self, viewset=None):
        self.vs = viewset
        self.children = []

    def add_node(self, node):
        if not self.vs and not node.vs.parent_viewset:
            self.children.append(node)
        elif self.vs and issubclass(self.vs, node.vs.parent_viewset):
            self.children.append(node)
        else:
            for child in self.children:
                child.add_node(node)

    def __repr__(self):
        if not self.vs:
            return "Root"
        else:
            return str(self.vs)

    def register_with(self, router):
        if self.vs and not self.vs.is_master_viewset():
            router.register(self.vs.urlpattern(), self.vs, self.vs.view_name())
            if self.children:
                router = routers.NestedDefaultRouter(router, self.vs.urlpattern(), lookup=self.vs.router_lookup)
                all_routers.append(router)
        for child in self.children:
            child.register_with(router)


all_viewsets = []
for app_config in pulp_plugin_configs():
    for viewset in app_config.named_viewsets.values():
        all_viewsets.append(viewset)

vs_tree = VSNode()
sorted_by_depth = sorted(all_viewsets, key=lambda vs: vs._get_nest_depth())
for vs in sorted_by_depth:
    # if vs.view_name().startswith("dist"):
    #     import ipdb; ipdb.set_trace()
    #     print(vs)
    vs_tree.add_node(VSNode(vs))

vs_tree.register_with(root_router)

urlpatterns = [
    url(r'^{}/'.format(ContentView.BASE_PATH), ContentView.as_view()),
    url(r'^api/v3/status/', StatusView.as_view()),
]

for each in all_routers:
    urlpatterns.append(url(r'^api/v3/', include(each.urls)))
