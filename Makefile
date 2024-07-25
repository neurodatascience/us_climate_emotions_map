.PHONY: get_submodule create_volume copy_data setup

setup: get_submodule create_volume copy_data

get_submodule:
	git submodule update --init --recursive

create_volume:
	docker volume create climate_data

copy_data:
	docker run --rm -v climate_data://dash/data -v $(PWD)/data:/source alpine cp -a /source/. /dash/data/
