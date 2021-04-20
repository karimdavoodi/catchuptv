
############# Build images ##############################

build_all: build_condent_publish build_condent_review build_condent_store build_general_domain build_user_managment

	
build_condent_store: dep
	docker build -t cs-live-to-hls -f src/condent_store/cs-live-to-hls/Dockerfile .
	docker build -t cs-live-cache-play   -f src/condent_store/cs-live-cache-play/Dockerfile .
	docker build -t cs-offline-play   -f src/condent_store/cs-offline-play/Dockerfile .
	docker build -t cs-mq-to-fs-db-cache -f src/condent_store/cs-mq-to-fs-db-cache/Dockerfile .

build_general_domain:
build_user_managment:
build_condent_publish:
build_condent_review:

dep:
	/bin/mk
############# Deploy  ##############################
dep_condent_store: dep
	kubectl apply -f dep/condent_store/cs-gb-config-map.yaml
	kubectl apply -f dep/condent_store/cs-gb-mq.yaml
	kubectl apply -f dep/condent_store/cs-db-seg.yaml
	kubectl apply -f dep/condent_store/cs-live-cache-play.yaml
	kubectl apply -f dep/condent_store/cs-offline-play.yaml
	kubectl apply -f dep/condent_store/cs-live-to-hls.yaml
	kubectl apply -f dep/condent_store/cs-fs-seg.yaml
	kubectl apply -f dep/condent_store/cs-persistent-storage.yaml

############# Delete  ##############################
del_condent_store: dep
	kubectl delete -f dep/condent_store

dep_test_pod:
	kubectl apply -f dep/condent_store/test-net-stream.yaml

dep_api_gateway: 
	kubectl apply -f dep/general_domain/api_gateway/kong.yaml
	kubectl apply -f dep/general_domain/api_gateway/ingress-general.yaml

