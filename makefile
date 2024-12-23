.PHONY: .env

.env:
	cp .env.example .env
	echo "init" >> .env