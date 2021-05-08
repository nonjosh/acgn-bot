start:
	docker build . -t nonjosh/acgn-bot
	kubectl apply -k k8s/base
rm:	
	kubectl delete -k k8s/base
	docker image rm nonjosh/acgn-bot
rebuild:
	kubectl delete -k k8s/base
	docker build . -t nonjosh/acgn-bot
	kubectl apply -k k8s/base
