"""pulp URL Configuration"""
from django.conf.urls import url, include
from rest_framework_nested import routers

from pulpcore.app.apps import pulp_plugin_configs
from pulpcore.app.views import ContentView, StatusView

import logging
log = logging.getLogger(__name__)


class VSNode(object):
    """
    This is a tree that can register nested ViewSets with DRF routers.
    """
    def __init__(self, viewset=None):
        self.vs = viewset
        self.children = []

    def add_node(self, node):
        """
        Add a VSNode to the tree.

        Some nodes must be added more than once. In the case of a Master/Detail parent,
        (example Distributions) the ViewSet's parent_viewset is a master viewset. Each of the detail
        viewsets belonging will have its own router, and the Distribution viewset must be registered
        with each of them.
        """
        # Master viewsets cannot be registered
        if node.vs.is_master_viewset():
            return
        # Non-nested viewsets are attached to the root node
        if not node.vs.parent_viewset:
            self.children.append(node)
        # link to all parent viewsets
        elif self.vs and issubclass(self.vs, node.vs.parent_viewset):
            self.children.append(node)
        else:
            for child in self.children:
                child.add_node(node)

    def register_with(self, router, all_routers=None):
        """
        Register this tree with the specified router. Returns a list of all rounters that are
        created.
        """
        if all_routers is None:
            all_routers = [router]
        # Root node does not need to be registered, and it doesn't need a router either.
        if self.vs:
            router.register(self.vs.urlpattern(), self.vs, self.vs.view_name())
            if self.children:
                router = routers.NestedDefaultRouter(router, self.vs.urlpattern(),
                                                     lookup=self.vs.router_lookup)
                all_routers.append(router)
        # If we created a new router for the parent, register the children with it
        for child in self.children:
            all_routers = child.register_with(router, all_routers)

        return all_routers

    def __repr__(self):
        if not self.vs:
            return "Root"
        else:
            return str(self.vs)


all_viewsets = []
for app_config in pulp_plugin_configs():
    for viewset in app_config.named_viewsets.values():
        all_viewsets.append(viewset)

sorted_by_depth = sorted(all_viewsets, key=lambda vs: vs._get_nest_depth())
vs_tree = VSNode()
for vs in sorted_by_depth:
    vs_tree.add_node(VSNode(vs))

root_router = routers.DefaultRouter(
    schema_title='Pulp API',
    schema_url='/api/v3'
)  #: The Pulp Platform v3 API router, which can be used to manually register ViewSets with the API.


urlpatterns = [
    url(r'^{}/'.format(ContentView.BASE_PATH), ContentView.as_view()),
    url(r'^api/v3/status/', StatusView.as_view()),
]

all_routers = vs_tree.register_with(root_router)
for each in all_routers:
    urlpatterns.append(url(r'^api/v3/', include(each.urls)))
