# Résumés de rencontres — Ubuntu / Docker / CPU

Interface française pour déposer un audio M4A, MP3, WAV, OGG, FLAC, AAC ou la piste audio d'un MP4. Produit une transcription horodatée et un compte rendu Markdown : résumé, sujets discutés, décisions, tableau des suivis et points à clarifier.

## Avec Dockhand (recommandé pour ce dépôt)

Suivez [le guide Dockhand](DOCKHAND.md) et choisissez **`compose.dockhand.yaml`** dans la stack Git. Les modèles sont préparés automatiquement; ne lancez pas `install.sh` pour ce parcours.

## Installation en ligne de commande (alternative)

Prérequis : Ubuntu x86-64 avec Docker Engine et Docker Compose v2 disposant de `up --wait`. L'utilisateur doit pouvoir exécuter Docker. Prévoir 8 à 16 Go de RAM au total, avec plusieurs Go réellement libres, et environ 10 Go de disque pour images et modèles. Avec Odoo et d'autres services sur le même hôte, 16 Go est préférable. La vitesse dépend fortement du CPU; aucune garantie de temps réel.

1. Décompressez l'archive sur Ubuntu et ouvrez le dossier `resume-local`.
2. Lancez :

```bash
bash install.sh
```

Le script construit l'image, télécharge Qwen3 4B et Whisper small, puis recrée le réseau Docker sans accès sortant. Internet est requis pendant cette préparation. Les volumes de modèles sont conservés. Une relance du script arrête uniquement ce projet pendant la préparation.

3. Depuis PowerShell sur votre PC Windows, ouvrez un tunnel (remplacez UTILISATEUR et IP_UBUNTU) :

```powershell
ssh -N -L 8501:127.0.0.1:8501 UTILISATEUR@IP_UBUNTU
```

4. Gardez ce terminal ouvert et visitez http://localhost:8501 dans votre navigateur Windows. Sur Ubuntu lui-même, cette même adresse est directement utilisable.

Le port est volontairement lié à 127.0.0.1 : aucune authentification applicative n'est intégrée. N'exposez pas directement ce port sur Internet. Pour un accès partagé par Traefik, prévoir une authentification et HTTPS avant de modifier le réseau. Cette archive cible Docker Compose, pas `docker stack deploy` / Swarm.

## Utilisation

Déposez un fichier de 200 Mo maximum, sélectionnez la langue puis cliquez sur « Transcrire et résumer ». Gardez la page ouverte pendant le traitement. Téléchargez les deux résultats avant de fermer la session. Un seul traitement s'exécute à la fois sur cette instance. Les vidéos servent uniquement à extraire la parole : aucune analyse des images ou captures d'écran.

L'audio temporaire est supprimé après transcription, y compris en cas d'erreur Python, et se trouve dans un tmpfs. Transcription et résumé restent en mémoire dans la session; aucun historique disque n'est créé par l'application. Le fichier téléversé peut rester dans la mémoire de la session jusqu'à son nettoyage. Le swap de l'hôte et les téléchargements du navigateur dépendent de votre configuration.

## Modèles et qualité

- faster-whisper `small`, CPU int8 : transcription multilingue, français par défaut.
- Ollama `qwen3:4b` : synthèse française, contexte limité à 8192 tokens pour maîtriser la RAM.
- Whisper fonctionne dans un sous-processus qui se termine avant la synthèse. Ollama décharge le modèle après chaque appel.
- Les longs textes sont résumés par sections, puis consolidés. Des détails peuvent être perdus; conservez la transcription comme source.
- Aucune identification automatique des intervenants. Les responsables et échéances ne sont renseignés que si le modèle les trouve dans les propos.
- Relisez les noms, chiffres, décisions et suivis avant diffusion. Un résumé peut contenir des erreurs malgré les instructions de fidélité.

## Exploitation

```bash
docker compose ps
docker compose logs --tail=100 app ollama
docker compose stop
docker compose start
```

Pour arrêter et retirer les conteneurs tout en gardant les modèles : `docker compose down`. Ne pas ajouter `-v` si vous souhaitez conserver les modèles.

En cas de téléchargement incomplet, relancez `bash install.sh`. En cas d'arrêt par manque de mémoire, libérez de la RAM ou réduisez les autres charges. Les modèles et versions choisies ne sont pas un engagement de performance sur votre serveur.

Les dépendances Python sont bornées par version majeure; l'image Ollama utilise `latest`. Pour figer une installation validée, notez les versions et digest effectivement installés avant toute mise à jour. Les mises à jour ne sont pas automatiques.

## Vérifications de cette livraison

Compilation syntaxique Python, syntaxe Bash et tests isolés du découpage, de la consolidation et des erreurs Ollama. Aucun test de transcription réelle ni démarrage Docker réalisé dans l'environnement de préparation (Docker indisponible). Premier essai conseillé : un audio non sensible de 1 à 2 minutes, avant une longue rencontre.

## Documentation officielle

- https://github.com/SYSTRAN/faster-whisper
- https://ollama.com/library/qwen3:4b
- https://docs.ollama.com/api
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml
