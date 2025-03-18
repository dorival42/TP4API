**TP : Comprendre et Modifier les Routes dans une API FastAPI et Remplacer une Lecture Fichier par une Lecture depuis une Base de Données**

---

### 1. **Objectifs Pédagogiques :**  
À la fin de ce TP, vous devez être capables de :  
1. Comprendre le fonctionnement des routes dans une application FastAPI.  
2. Modifier ou ajouter des routes dans une application existante.  
3. Utiliser une base de données PostgreSQL pour remplacer un fichier source existant comme méthode de stockage.  
4. Remplacer les operations sur dataframe pandas par des requettes sql avec SQLalchemy

---

### 2. **Contexte et Motivation :**  

FastAPI est un framework très populaire pour construire des API performantes et modernes en Python. Dans une application réelle, la gestion des données via un fichier (par exemple JSON ou CSV) est utile pour les prototypes, mais inadéquate pour les projets en production. L'utilisation d'une base de données relationnelle est alors essentielle pour fiabiliser et optimiser les interactions avec les données.  

Dans ce TP, vous allez explorer les routes existantes d'une application FastAPI, les modifier selon des exigences spécifiques, et implémenter une solution avec une base de données pour remplacer la lecture/écriture depuis un fichier.  

La base de données et l'app seront deployer avec docker compose (fichier déjà existant)

Docker Compose est un outil puissant pour définir et gérer des applications multi-conteneurs Docker. Il vous permet de créer, configurer et exécuter plusieurs conteneurs en utilisant un simple fichier de configuration appelé docker-compose.yml. Cela simplifie grandement le déploiement d'applications complexes qui nécessitent plusieurs services interconnectés (par exemple, une application web, une base de données, un cache, etc.).

Pourquoi utiliser Docker Compose ?
Docker Compose simplifie la gestion des conteneurs dans plusieurs cas d'usage :

Déploiement d'applications : Il est courant qu'une application soit constituée de plusieurs services (par exemple, une API serveur, une base de données, et un serveur d'authentification). Compose vous évite d'exécuter chaque conteneur manuellement en ligne de commande.
Isolation des environnements : Vous pouvez facilement créer des environnements de développement, de test ou de production spécifiques, avec toutes leurs configurations.
Simplicité d'utilisation : Une seule commande permet de démarrer tous les services définis dans le fichier docker-compose.yml.

---

### 3. **Énoncé du Problème :**  
Vous êtes chargé de maintenir une application qui expose des API REST via FastAPI. Cette application utilise actuellement un fichier u.data pour lire et stocker des données. Un collègue a déjà implémenté des routes permettant de manipuler les données, mais vous devez effectuer les tâches suivantes :  
1. Comprendre les routes existantes (explorer leur rôle et comportement).  
2. Ajouter ou modifier une route pour répondre à un nouveau besoin.  
3. Migrer le stockage des données depuis le fichier base de données PostgresSQL.  

Vous concentrerez vos efforts sur :  
- Une route principale qui retourne une liste d’éléments.  
- Une route qui permet d’ajouter un élément à cette liste.  
- Assurer que les nouvelles fonctionnalités interagissent correctement avec SQLite.  

---



### 4. **Tâches à Réaliser :**  



#### Étape 1 : **Configuration de l’environnement**  
1. Lancez les services PostgreSQL et L'app en utilisant docker compose avec la commande :
```bash
 docker compose up -d
# si la commande docker compose ne marche pas lancer la commande 
docker-compose up -d
```
2. Expliquez comment l'application ce lancer. Regardez le Dockerfile à l'intérieur du dossier app. Quelle commande il execute ?  

#### Étape 2 : **Comprendre les routes existantes**  
- Identifiez les routes déjà implémentées et testez-les avec Swagger UI (la route /docs).  
- Notez leur comportement : quelles entrées elles acceptent, quelles données elles retournent, et leur interaction avec le fichier data

#### Étape 3 : **Modifier ou ajouter une route**  
- Ajoutez une nouvelle route `GET /user/{user_id}/details` qui permet de récupérer un élément les information sur un utilisateur grâce à son `id`. Si l'élément n'existe pas, renvoyez une erreur 404 avec un message clair.  


#### Étape 4 : **Migration vers une base de données PostgreSQL**  
Nous volons plus utiliser le fichier u.data distant. On souahite charger deux fichier `rantings.csv` qui rempalce le fichier `u.data`, un fichier `movies_metadata.csv`. Ces fichier à récupérer [iciL](https://drop.chapril.org/download/9ad1ecf72cbf9170/#rddjNC0C0Scg5EObwm00_w). L'objectif et de faire la jointure entre les deux fichier avec des requettes SQL lors de l'appel de la route `recommand`
pour que les prédictions rendent des nom de film au lieux des leur ids.

1. Analysez les fichiers py présents dans le dossier `postgresql`. Ils utilisent SQLAlchemy pour faire intéragir les objets python avec la base de données.
2. Quel est le lien entre les paramètres de la fonction `get_db_engine` dans import_data.py avec `api.environment` dans le fichier `docker-compose.yml`.
3. lancer le script `import_data.py`, il permet d'injecter les csv dans la base de donner. sous forme de deux tables.
4. Inspirer vous de fichier d'injection pour créer des fonction de lecture et jointure dans l'application. Cela nous permettera d'utiliser la base de donné avec l'api au lieu du fichier.

#### Étape 5 : **Validation des modifications**  
- Vérifiez que toutes les routes fonctionnent correctement avec la base de données. 
- Debugez si nécessaire

