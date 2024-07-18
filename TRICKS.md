# copy docker files on initcontainers
#  initContainers:
#    - name: copy-config
#      image: kerberos/agent:latest
#      securityContext:
#        runAsUser: 0
#      command: [ '/bin/sh', '-c', 'cp -R /home/agent/data/* /tmp/' ]
#      volumeMounts:
#        - name: kerberos-agent-hallway-data
#          mountPath: /tmp