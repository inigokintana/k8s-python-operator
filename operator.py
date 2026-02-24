import kopf
from kubernetes import client, config

# Load the Kubernetes configuration (for local development)
config.load_kube_config()

# Define the handler for creating the 'MyApp' resource
@kopf.on.create('myapp.example.com', 'v1', 'myapps')
def on_create(spec, name, namespace, logger, **kwargs):
    logger.info(f"Creating MyApp {name} in namespace {namespace}")
    # Example action: create a ConfigMap as part of the operator action
    api = client.CoreV1Api()
    config_map = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(name=f"config-{name}", namespace=namespace),
        data={"app_name": name, "spec": str(spec)},
    )
    api.create_namespaced_config_map(namespace, config_map)
    logger.info(f"ConfigMap created for MyApp {name}")

# Define a handler for updating the 'MyApp' resource
@kopf.on.update('myapp.example.com', 'v1', 'myapps')
def on_update(spec, name, namespace, logger, **kwargs):
    logger.info(f"Updating MyApp {name} in namespace {namespace}")
    # You could perform an action here, like updating a service or config map
    logger.info(f"New spec: {spec}")

# Define a handler for deleting the 'MyApp' resource
@kopf.on.delete('myapp.example.com', 'v1', 'myapps')
def on_delete(name, namespace, logger, **kwargs):
    logger.info(f"Deleting MyApp {name} in namespace {namespace}")
    # Example action: delete the associated ConfigMap
    api = client.CoreV1Api()
    api.delete_namespaced_config_map(name=f"config-{name}", namespace=namespace)
    logger.info(f"ConfigMap deleted for MyApp {name}")