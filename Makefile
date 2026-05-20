COMPOSE ?= docker compose
BOTS = pain konan itachi kisame deidara sasori hidan kakuzu tobi zetsu
ALL_BOTS = coordinator $(BOTS)

.PHONY: help up down restart build rebuild logs logs-bots ps clean \
        bot-% logs-% restart-% rebuild-%

help:
	@echo "Akatsuki bots — make targets:"
	@echo "  up              start everything (-d)"
	@echo "  down            stop and remove containers"
	@echo "  restart         restart all services"
	@echo "  build           build images (cache ok)"
	@echo "  rebuild         build --no-cache for all bots + coordinator, then up -d"
	@echo "  ps              show container status"
	@echo "  logs            tail logs for everything"
	@echo "  logs-bots       tail logs for coordinator + 10 bots (no redis/portainer)"
	@echo "  logs-<name>     tail logs for a single service (e.g. logs-pain)"
	@echo "  restart-<name>  restart a single service (e.g. restart-pain)"
	@echo "  rebuild-<name>  --no-cache rebuild + restart a single service"
	@echo "  clean           down + remove built images"

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) build --no-cache $(ALL_BOTS)
	$(COMPOSE) up -d

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f --tail=100

logs-bots:
	$(COMPOSE) logs -f --tail=100 $(ALL_BOTS)

logs-%:
	$(COMPOSE) logs -f --tail=200 $*

restart-%:
	$(COMPOSE) restart $*

rebuild-%:
	$(COMPOSE) build --no-cache $*
	$(COMPOSE) up -d $*

clean:
	$(COMPOSE) down --rmi local
