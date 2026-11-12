# Accès HTTPS via Traefik

Adresse proposée : **https://whisper.allanot.ovh**. Aucun changement DNS ou déploiement n'est effectué par l'ajout de ces fichiers.

## Même hôte Docker

Dans la stack Git Dockhand existante, conservez son nom actuel et changez uniquement le fichier Compose pour **compose.traefik.yaml**. Activez le build et synchronisez le dépôt complet, y compris `traefik/nginx.conf`. Conserver le nom de stack permet de réutiliser les volumes de modèles. Ne créez pas une deuxième stack concurrente.

Variables Dockhand (adapter aux noms réels de votre Traefik) :

```env
WHISPER_DOMAIN=whisper.allanot.ovh
TRAEFIK_NETWORK=traefik-public
TRAEFIK_ENTRYPOINT=websecure
TRAEFIK_CERTRESOLVER=ovh
TRAEFIK_AUTH_MIDDLEWARE=whisper-auth@file
```

Le réseau externe doit déjà exister et Traefik doit y être connecté. S'il s'agit d'un réseau Swarm overlay, il doit être **attachable** pour ces conteneurs Compose. Le provider **Docker** de Traefik doit découvrir ce serveur; les labels sont sur les conteneurs, pas des services Swarm.

La passerelle Nginx est seule connectée au réseau Traefik. L'application et Ollama restent sur le réseau interne. Aucun port 8501 n'est publié dans cette variante. Les WebSockets Streamlit passent par la passerelle.

Dockhand doit rendre le montage relatif `./traefik/nginx.conf` disponible sur l'hôte Docker. En environnement distant, vérifier la synchronisation des fichiers avec Hawser. Un fichier absent ou monté comme répertoire empêche Nginx de démarrer.

## Authentification

Si vous possédez déjà un middleware d'authentification, utilisez son nom qualifié (par exemple `mon-auth@file`) dans `TRAEFIK_AUTH_MIDDLEWARE`.

Sinon, créez un fichier htpasswd sur le serveur Traefik avec l'outil `htpasswd` (paquet Ubuntu `apache2-utils`) :

```bash
htpasswd -cB whisper.htpasswd nicolas
```

La commande demande le mot de passe sans l'inscrire dans l'historique. Utilisez `-c` seulement pour un nouveau fichier. Montez le fichier créé en lecture seule dans le conteneur Traefik à `/etc/traefik/auth/whisper.htpasswd`. Copiez le contenu de `traefik/auth.example.yaml` dans son répertoire dynamique surveillé. Ce répertoire dépend de votre configuration existante : ne remplacez pas sa configuration statique.

Le middleware par défaut est obligatoire : s'il est absent, la route ne fonctionne pas, au lieu d'exposer l'application sans authentification. Ne commitez pas le fichier htpasswd ni les identifiants OVH.

## DNS et HTTPS

Créez l'enregistrement DNS de `whisper.allanot.ovh` vers le point d'entrée de votre Traefik (ou réutilisez votre wildcard existant). La résolution locale doit aussi aboutir à ce Traefik. Le resolver `ovh` doit déjà être configuré dans Traefik. Ne recopiez pas de secrets OVH dans cette stack.

Redéployez ensuite la stack et ouvrez https://whisper.allanot.ovh. Ce fichier fournit uniquement la route HTTPS; une redirection HTTP vers HTTPS peut rester gérée globalement par votre Traefik.

## Traefik sur un autre serveur

Un réseau portant le même nom sur deux hôtes indépendants n'est pas un réseau partagé. Les labels du serveur Whisper ne sont pas automatiquement découverts par le provider Docker de l'autre serveur.

Dans ce cas, conservez `compose.dockhand.yaml`, avec `BIND_IP` égal à l'IP LAN du serveur Whisper et `APP_PORT=8501`. Copiez `traefik/remote.example.yaml` dans le répertoire dynamique de votre Traefik, remplacez `IP_UBUNTU_WHISPER` et ajustez domaine, entrypoint et resolver. Installez également le middleware d'authentification décrit ci-dessus. N'activez pas simultanément la variante Docker.

Le port 8501 du serveur Whisper doit être joignable depuis Traefik seulement, via des règles réseau/pare-feu adaptées aux ports publiés Docker. Sinon, un accès LAN direct contournerait l'authentification Traefik. Le trafic entre hôtes utilise ici HTTP sur un réseau privé de confiance; utilisez un tunnel privé si ce réseau ne l'est pas. Aucune exposition de docker.sock n'est nécessaire.

## Diagnostic

- 404 : route non découverte, Host/DNS incorrect ou middleware absent; consulter les logs Traefik.
- 502/504 : réseau externe, IP distante, disponibilité de app ou passerelle à vérifier.
- Certificat incorrect : vérifier DNS, nom du resolver et journaux ACME.
- Téléversement interrompu : vérifier limites et délais des autres proxies et de l'entrypoint Traefik. La limite applicative reste 200 Mo.
- Les conteneurs init doivent finir avec code 0; app, ollama et (variante même hôte) gateway doivent rester actifs.

Validation à la préparation : syntaxe YAML et cohérence de la configuration. Aucun déploiement réel Traefik/Docker effectué.

Références : https://doc.traefik.io/traefik/providers/docker/ et https://doc.traefik.io/traefik/providers/file/
