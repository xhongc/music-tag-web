from rest_framework.routers import DefaultRouter

from . import views

flow_router = DefaultRouter()
flow_router.register(r"flow", viewset=views.ProcessViewSets, base_name="flow")
flow_router.register(r"run", viewset=views.ProcessRunViewSets, base_name="run")
flow_router.register(r"sub_run", viewset=views.SubProcessRunViewSets, base_name="sub_run")
flow_router.register(r"test", viewset=views.TestViewSets, base_name="test")

node_router = DefaultRouter()
node_router.register(r"template", viewset=views.NodeTemplateViewSet, base_name="template")
