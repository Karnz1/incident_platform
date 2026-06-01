{{/* Generate basic labels */}}
{{- define "my-app.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
environment: {{ .Values.envName | default "dev" }}
{{- end -}}