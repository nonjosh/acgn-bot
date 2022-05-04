setup:
	docker build . -t nonjosh/acgn-bot
	kubectl apply -f k8s/secrets/k8s-secrets.yaml
	kubectl create configmap acgn-bot.list.yaml --from-file=config/list.yaml --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -k k8s/base
rm:
	kubectl delete -k k8s/base
	kubectl delete configmap acgn-bot.list.yaml
	kubectl delete -f k8s/secrets/k8s-secrets.yaml
	docker image rm nonjosh/acgn-bot
rebuild:
	kubectl delete -k k8s/base
	docker build . -t nonjosh/acgn-bot
	kubectl apply -k k8s/base
