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

def routers_for_nested_viewset(viewset):
    """
    Find the router for a nested viewset.

    Args:
        viewset (pulpcore.app.viewsets.NamedModelViewSet): a viewset for which a nested router
            should exist

    Returns:
        routers.NestedDefaultRouter: the nested router whose parent_prefix corresponds to the
            viewset's nest_prefix attribute.

    Raises:
        LookupError: if no nested router is found for the viewset.

    """
    if viewset.nest_prefix:

        # must have nest_prefix if you have parent_viewset
        if viewset.parent_viewset.is_master_viewset():
            extra_regex = "\/.+"
        else:
            extra_regex = ""

        regex = re.compile("^{prefix}{detail_type}".format(prefix=viewset.nest_prefix, detail_type=extra_regex))
        routers = []
        for router in all_routers:
            if hasattr(router, 'parent_prefix') and re.search(regex, router.parent_prefix):
                routers.append(router)
        # routers = [r for r in nested_routers if re.search(regex, r.parent_prefix)]
        # router_prefixes = [router.parent_prefix for router in nested_routers]
        # routers_to_register_with = filter(regex.match, router_prefixes)
        return routers
    else:
        return [root_router]


viewsets_by_depth = collections.defaultdict(list)
for app_config in pulp_plugin_configs():
    for viewset in app_config.named_viewsets.values():
        viewsets_by_depth[viewset._get_nest_depth()].append(viewset)

for depth in sorted(viewsets_by_depth.keys()):
    for viewset in viewsets_by_depth[depth]:
        for router in routers_for_nested_viewset(viewset):
            new_router = viewset.register_with(router)
            if new_router:
                all_routers.append(new_router)

urlpatterns = [
    url(r'^content/', ContentView.as_view()),
    url(r'^api/v3/status/', StatusView.as_view()),
]

for each in all_routers:
    urlpatterns.append(url(r'^api/v3/', include(each.urls)))

# nested_routers = [
#     routers.NestedDefaultRouter(root_router, 'repositories', lookup='repository'),
# ]



        #
        # # Router: (router, urlpattern, lookup)
        # regex = r"^publisher\/.+$"
        # matches = re.finditer(regex, test_str)
        #
        #
        # if nrouter.parent_prefix == "/".join(viewset.get_endpoint_pieces()):
        #     return nrouter
        # Not ideal, but == doesnt work for nested detail viewsets like FilePublisher publishers/file'
        # elif nrouter.parent_prefix.startswith(viewset.nest_prefix):
        #     import ipdb; ipdb.set_trace()
            # return nrouter
        # Better way in progress:
        # for viewset_tuple in nrouter.parent_router.registry:
        #                      #prefix                                      VS                              base_name
        #     # tuple -> ('repositories', <class 'pulpcore.app.viewsets.repository.RepositoryViewSet'>, 'repositories')
        #     if issubclass(viewset_tuple[1], viewset.parent_viewset):
        #         import ipdb; ipdb.set_trace()
        #         return nrouter

    # import ipdb; ipdb.set_trace()
    # raise LookupError()#'No nested router has prefix {}'.format(viewset.nest_prefix))


# # go through nested viewsets and register them
# double_nested = []
# try:
#     for app_config in pulp_plugin_configs():
#         for viewset in app_config.named_viewsets.values():
#             if viewset.nest_prefix and not viewset.is_master_viewset():
#             #     if viewset.nest_prefix == 'publishers':
#             #         double_nested.append(viewset)
#             #         continue
#                 # if not viewset.is_master_viewset():
#                 #     import ipdb
#                 #     ipdb.set_trace()
#                 # import ipdb; ipdb.set_trace()
#                 try:
#                     router = router_for_nested_viewset(viewset)
#                 except LookupError as e:
#                     double_nested.append(viewset)
#                     continue
#
#                 new_router = viewset.register_with(router)
#                 if new_router:
#                     nested_routers.append(new_router)
#                     print(new_router)
#     #
#     for viewset in double_nested:
#         router = router_for_nested_viewset(viewset)
#         new_router = viewset.register_with(router)
#
#
#
#
# except AppRegistryNotReady as ex:
#     # urls is being imported outside of an initialized django project, probably by a docs builder
#     # or something else trying to inspect this module. Instead of exploding here and preventing the
#     # import from succeeding, throw a warning explaining what's happening.
#     warnings.warn("Unable to register plugin viewsets with API router, {}".format(ex.args[0]))
# #
#
#
#































# def ordered_viewset_registration_ancestry(viewsets, register_order=None):
#     more_nested = []
#     if register_order is None:
#         register_order = [None]
#
#     import ipdb; ipdb.set_trace()
#     for viewset in viewsets:
#         #already there
#         if viewset in register_order or viewset.is_master_viewset():
#             continue
#         # this viewset is a leaf
#         elif viewset.parent_viewset is None:
#             register_order.append(viewset)
#             continue
#
#         # ancestry is taken care of, time to add this one
#         elif viewset.parent_viewset in register_order:
#             register_order.append(viewset)
#             continue
#         else:
#             # we cant register with parent, we have to register with detail models of the parent
#             if viewset.parent_viewset.is_master_viewset() and viewset.parent_viewset not in more_nested:
#                 more_nested.append(viewset)
#                 continue
#             else:
#                 # parent exists, but is not ordered yet. recursively do that.
#                 parent_order = ordered_viewset_registration_ancestry([viewset.parent_viewset, viewset], register_order)
#                 register_order = register_order + parent_order
#     final_order = ordered_viewset_registration_ancestry(more_nested, register_order)
#     return final_order
#

# later = []
# def order_vs(vs, current_order):
#     if vs in current_order:
#         return current_order
#     elif vs.is_master_viewset():
#         return current_order
#     else:
#         if vs.parent_viewset is None:
#             return current_order + [vs]
#         else:
#             if vs.parent_viewset in current_order:
#                 return current_order + [vs]
#             else:
#                 if vs.parent_viewset.is_master_viewset():
#                     for ordered in current_order:
#                         if issubclass(ordered, vs.parent_viewset):
#                             return current_order + [vs]
#                     else:
#                         later.append(vs)
#                         return current_order
#                 else:
#                     rec = order_vs(vs.parent_viewset, current_order)
#                     return order_vs(vs, rec)

    #
    #
    #
    # elif vs.parent_viewset in current_order:
    #     if vs.is_master_viewset():
    #         print("Vthis is my problem")
    #         print(vs)
    #         print("^this is my problem")
    #         return current_order 
    #     else:
    #         current_order.append(vs)
    #         return current_order
    # else:
    #     import ipdb; ipdb.set_trace()
    #     current_order = order_vs(vs.parent_viewset, current_order)
    #     return order_vs(vs, current_order)
    #
# current_order = []
# for vs in all_viewsets:
#     current_order = order_vs(vs, current_order)
#
# for vs in later:
#     current_order = order_vs(vs, current_order)
#
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# print("ORDER_________________________________")
# pprint(current_order)
#
#
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# print("laterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
# pprint(later)
#
#
#
#
#
#     if viewset in viewset_registration_order:
#         continue
#     if getattr(viewset, 'parent_viewset'):
#         if viewset.parent_viewset in viewset_registration_order:
#             continue
#
#
#     # TODO(asmacdo)check for parent viewset, register it instead
#     # Or not, parent viewsets might be master viewsets :(
#     if viewset.parent_viewset:
#
