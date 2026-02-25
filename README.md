# TOC (Table of Contents)

1. [Objective](#1---objective)
    - [Why is this so powerful?](#11-why-is-this-so-powerful)
2. [Let's see the theory behind](#2---lets-see-the-theory-behind)
    - [CRDs: How Kubernetes Lets You Create New APIs](#21-crds-how-kubernetes-lets-you-create-new-apis)
    - [Controllers/Operator: Attaching Behavior to Your New API](#22-controllersoperator-attaching-behavior-to-your-new-api)
    - [Python Kopf vs Go](#23-python-kopf-vs-go)
3. [Steps to create my 1st K8s API & Operator](#3---steps-to-create-my-1st-k8s-api--operator)
    - [Install Python dependencies](#31-install-python-dependencies)
    - [Custom Resource Definition (CRD)](#32-custom-resource-definition-crd)
    - [Create a Simple Controller/Operator](#33-create-a-simple-controlleroperator)
    - [Run the Operator](#34-run-the-operator)
    - [CRUD Custom Resource to trigger the operator/controller logic](#35-crud-custom-resource-to-trigger-the-operatorcontroller-logic)
4. [References](#4---references)
# 1 - Objective
Build a controller/operator for k8s using Python Kopf (Kubernetes Operator  Python Framework). Kopf is a Python framework that helps you build Kubernetes controllers/operators in a simple and declarative way.  This is a  is a great choice, especially if you want to avoid the steep learning curve of Go and the official operator-sdk.

When people say **“K8S is the API to make APIs”**, they usually mean this:
 - Kubernetes itself is an API server that lets you define new APIs (via CRDs) and attach behavior to them (via controllers/operators).
 - At its core,  Kubernetes container orchestration system, is a REST API backed by etcd (state storage) with controllers/operators reconciling desired state of a CR (Custom Resource).


## 1.1) Why is this so powerful?
- Instead of writing: Terraform modules, Bash automation, Ansible scripts, CI/CD glue ...
- You define: a KafkaCluster or postgresCluster CRD with its controller/operator and Kubernetes handles:
    - Provisioning
    - Scaling
    - Self-healing
    - Upgrades
    - Drift correction

So, Infrastructure becomes declarative APIs and extending Kubernetes into a platform for building platforms. Some real-World examples are:
- "Prometheus Operator","kubernetes monitoring operator". Adds ServiceMonitor and Prometheus APIs
- "Argo CD","continuous delivery tool". Adds Application API for GitOps
- "Crossplane","kubernetes infrastructure control plane". Turns cloud infrastructure (RDS, S3, etc.) into Kubernetes APIs
- "Strimzi","kafka operator for kubernetes". Adds Kafka as a Kubernetes API
- ...


# 2- Let's see the theory behind

- Kubernetes = API server
- CRDs = API definitions
- Controllers/ Operators = automation engine business logic
- CR = an instance of the CRD - desired states
- etcd = state storage
- Reconciliation loop  = act of computing the delta between desired state in CR and observed state, then taking actions to close that gap = = automation engine in controller/operator

It’s not just a container orchestrator. It’s a distributed control plane framework.


## 2.1) CRDs: How Kubernetes Lets You Create New APIs
The real magic is: 👉 You can extend Kubernetes with Custom Resource Definitions (CRDs).

A CRD lets you define a brand new Kubernetes API type like:

````
kind: MyDatabase
kind: KafkaCluster
kind: MLTrainingJob
````
After applying a CRD and creating the corresponding CR Kubernetes now supports:

````
kubectl get mydatabases
````
That means you just added a new API endpoint to Kubernetes. That’s why people say "Kubernetes is a framework for building APIs."

## 2.2) Controllers/Operator: Attaching Behavior to Your New API
Creating a CRD only defines the API schema. To make it useful, you add/program a controller/operator that:
- Watches your custom resource CR
- Reconciles desired state
- Creates underlying objects (Pods, Services, etc.) inside K8S
For example:
````
kind: PostgresCluster
spec:
  replicas: 3
  version: 16
````
Your operator translates that into: StatefulSets, Services, PVCs, Backups, Failover logic

Now Kubernetes is not just managing containers… Your are extending K8S and it is managing databases as an API.

## 2.3) Python Kopf vs Go
You can write the Controller/operator using:
- Python Kopf (Kubernetes Operator Framework for Python).
- Go and the official operator-sdk.

**Comparison Table** 
|Feature | Python (Kopf) |Go (Operator-SDK) |
| -------- | ------- | ------- |
| Learning Curve |	Easy (hours) | Steep (weeks)
| Performance |	Moderate | High
| Industry Standard | 	No (Niche/Internal)	| Yes (De-facto standard)
| Community Support |	Good (Independent)	| Excellent (Official K8s/CNCF)
|Primary Use Case |	Internal automation, Glue |	Complex stateful apps, SaaS products

**Conclusion:**
- Python + Kopf is ideal for quick, less complex operators where development speed and simplicity are priorities.
- Go + Operator SDK is better suited for larger-scale, more complex operators, especially if you need high performance, scalability, or deep integration with the Kubernetes ecosystem.


# 3 - Steps to create my 1st K8s API & Operator

- Designing a new API - CRD
- Implementing reconciliation logic - Controller / Operator
- Run the controller / operator
- Defining API instance or desired state - CR

## 3.1) Install Python dependencies
You’ll need Python and pip to install the necessary libraries. Use of venv module is highly recommended.

````
pip install kopf kubernetes
````

## 3.2)  Custom Resource Definition (CRD)
A CRD is what Kubernetes uses to define custom resources (CR).

You can create a CRD file like this:

````
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: myapps.myapp.example.com
spec:
  group: myapp.example.com
  names:
    kind: MyApp
    plural: myapps
    singular: myapp
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                description:
                  type: string
````                
You can apply this CRD with kubectl:
````
kubectl apply -f myapp-crd.yaml
kubectl get crd myapps.myapp.example.com
````
## 3.2) Create a Simple Controller/Operator
We'll create an operator that listens to a custom MyApp resource and logs its creation.

operator.py:
 
````
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
`````


## 3.3) Run the Operator
Once your operator code and CRD are set up, you can run your operator. In the terminal, navigate to the directory containing operator.py and run the operator:
````
kopf run operator.py
````
The operator will now start watching for changes to MyApp resources and act accordingly.

## 3.4) CRUD Custom Resource to trrigger the operator/controller logic
Finally, you can create an instance of MyApp to test the operator. Here's an example YAML:
````
apiVersion: myapp.example.com/v1
kind: MyApp
metadata:
  name: my-first-app
  namespace: default
spec:
  description: "This is my first app created using an operator"
````
CRUD MyApp instance and see contoller/operator output:
````
Create:
  kubectl create -f myapp-instance.yaml
Update:
  kubectl apply -f myapp-instance.yaml
Delete:
  kubectl delete  -f myapp-instance.yaml
````

Controller/operator log output:
````
kopf run operator.py
/home/inigokintana/k8s-python-operator/.venv/lib/python3.12/site-packages/kopf/_core/reactor/running.py:179: FutureWarning: Absence of either namespaces or cluster-wide flag will become an error soon. For now, switching to the cluster-wide mode for backward compatibility.
  warnings.warn("Absence of either namespaces or cluster-wide flag will become an error soon."
[2026-02-25 09:49:03,319] kopf._core.engines.a [INFO    ] Initial authentication has been initiated.
[2026-02-25 09:49:03,322] kopf.activities.auth [INFO    ] Activity 'login_via_client' succeeded.
[2026-02-25 09:49:03,322] kopf._core.engines.a [INFO    ] Initial authentication has finished.
[2026-02-25 09:58:48,907] kopf.objects         [INFO    ] [default/my-first-app] Updating MyApp my-first-app in namespace default
[2026-02-25 09:58:48,908] kopf.objects         [INFO    ] [default/my-first-app] New spec: {'description': 'This is my second app created using an operator'}
[2026-02-25 09:58:48,909] kopf.objects         [INFO    ] [default/my-first-app] Handler 'on_update' succeeded.
[2026-02-25 09:58:48,909] kopf.objects         [INFO    ] [default/my-first-app] Updating is processed: 1 succeeded; 0 failed.
[2026-02-25 10:00:38,979] kopf.objects         [INFO    ] [default/my-first-app] Deleting MyApp my-first-app in namespace default
[2026-02-25 10:00:38,998] kopf.objects         [INFO    ] [default/my-first-app] ConfigMap deleted for MyApp my-first-app
[2026-02-25 10:00:38,999] kopf.objects         [INFO    ] [default/my-first-app] Handler 'on_delete' succeeded.
[2026-02-25 10:00:38,999] kopf.objects         [INFO    ] [default/my-first-app] Deletion is processed: 1 succeeded; 0 failed.
[2026-02-25 10:01:16,245] kopf.objects         [INFO    ] [default/my-first-app] Creating MyApp my-first-app in namespace default
[2026-02-25 10:01:16,258] kopf.objects         [INFO    ] [default/my-first-app] ConfigMap created for MyApp my-first-app
[2026-02-25 10:01:16,259] kopf.objects         [INFO    ] [default/my-first-app] Handler 'on_create' succeeded.
[2026-02-25 10:01:16,259] kopf.objects         [INFO    ] [default/my-first-app] Creation is processed: 1 succeeded; 0 failed.
[2026-02-25 10:01:40,918] kopf.objects         [INFO    ] [default/my-first-app] Updating MyApp my-first-app in namespace default
[2026-02-25 10:01:40,919] kopf.objects         [INFO    ] [default/my-first-app] New spec: {'description': 'This is my 3rd app created using an operator'}
[2026-02-25 10:01:40,919] kopf.objects         [INFO    ] [default/my-first-app] Handler 'on_update' succeeded.
[2026-02-25 10:01:40,920] kopf.objects         [INFO    ] [default/my-first-app] Updating is processed: 1 succeeded; 0 failed.

````

# 4 - References
- Hackernoon [deeper Kubernetes Operators explained](https://hackernoon.com/kubernetes-operators-explained-by-a-production-engineer)
- ChatGPT
- Gemini