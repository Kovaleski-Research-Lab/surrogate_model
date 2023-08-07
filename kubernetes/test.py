import subprocess

from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

for i in range(1000):
    pod_list = v1.list_namespaced_pod(namespace = "gpn-mizzou-muem")
    print(i) 

pod_phases = [item.status.phase for item in pod_list.items]
output = [1 for ele in pod_phases if(ele == "Succeeded")]

print(pod_phases, output)

"""
current_group = [ele.metadata.owner_references[0].name for ele in pod_list.items if("sim" in ele.metadata.name)]

current_group = list(set(current_group))

for job_name in current_group:
    subprocess.run(["kubectl", "delete", "job", job_name])

print("\nCleaned up any jobs that include tag : %s\n" % "sim")
"""
