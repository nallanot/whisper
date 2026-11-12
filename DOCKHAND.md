# Déploiement avec Dockhand

Dans Dockhand, sélectionnez l'environnement Docker Ubuntu cible puis **Stacks → From Git** (l'intitulé peut varier selon la version).

| Réglage | Valeur |
| --- | --- |
| Dépôt | `https://github.com/nallanot/whisper.git` |
| Branche | `main` |
| Nom de stack | `whisper` |
| Fichier Compose | `compose.dockhand.yaml` |
| Construction des images / Build | Activée |
| Mise à jour automatique | Désactivée pour le premier essai |

Déployez la stack depuis Git, avec le dépôt complet comme contexte de construction. Ne collez pas seulement le YAML dans l'éditeur : le Dockerfile et les fichiers `app/` sont nécessaires. Si votre Dockhand/Hawser ne sait pas transmettre le contexte de build au serveur distant, mettez-les à jour ou utilisez l'installation CLI décrite dans le README.

## Premier démarrage

1. `ollama-init` télécharge Qwen3 4B dans son volume.
2. `whisper-init` télécharge et vérifie Whisper small dans son volume.
3. Ces deux conteneurs se terminent avec le code **0** : c'est normal, ils ne restent pas actifs.
4. `ollama` et `app` démarrent après la préparation. Ils utilisent un réseau Docker interne sans accès Internet sortant.

Le téléchargement et la construction peuvent durer plusieurs minutes. Suivez les journaux des deux services `*-init`. Si l'interface Dockhand atteint son délai d'attente, vérifiez les journaux et l'état réel des conteneurs avant de relancer. Ne supprimez pas les volumes de modèles. Aux redéploiements, les poids en cache sont réutilisés.

## Ouvrir l'interface depuis Windows

Par défaut, le service écoute seulement sur la boucle locale du serveur. Dans PowerShell :

```powershell
ssh -N -L 8501:127.0.0.1:8501 UTILISATEUR@IP_UBUNTU
```

Gardez ce terminal ouvert et visitez **http://localhost:8501**.

Pour un accès direct sur un réseau local de confiance, définissez dans les variables de déploiement Dockhand `BIND_IP` sur l'adresse LAN réelle du serveur Ubuntu, puis redéployez. Ouvrez `http://IP_UBUNTU:8501`. `APP_PORT` permet de changer le port. L'application n'a pas d'authentification : l'accès LAN est réservé aux utilisateurs de confiance. N'ouvrez pas ce port sur le routeur. Pour Traefik, une configuration séparée avec HTTPS et authentification est nécessaire.

## Vérification

Déposez d'abord un enregistrement non sensible de 1 à 2 minutes. Vérifiez la transcription, puis téléchargez le compte rendu. Aucun enregistrement, modèle ou secret n'est stocké dans GitHub.

Cette configuration cible Docker Compose (y compris sur un hôte ayant Swarm activé), pas `docker stack deploy`. Ne lancez pas `install.sh` pour ce parcours : Dockhand exécute les initialisations.

Documentation : https://dockhand.pro/manual/
