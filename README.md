# LikeToMoveIt.py

## Description du programme

Le présent programme constitue un **dispositif expérimental de stimulation cinématique** destiné à provoquer, sous contrôle temporel, une **mobilité exogène** du pointeur de souris au sein d’un environnement graphique. L’objectif n’est pas d’“automatiser” un déplacement au sens fonctionnel, mais de mettre en œuvre un **protocole d’injection de trajectoires** afin d’observer la réponse d’un système de pointage et de sa chaîne logicielle (gestion d’événements, boucle UI, serveur d’affichage, politiques de lissage et de temporisation).

L’application se compose de deux sous-systèmes couplés :

1. **Un module d’orchestration temporelle** (interface Tkinter) assurant la définition d’une fenêtre expérimentale de durée (T) (en minutes), la visualisation d’un décompte résiduel, et la gestion d’états finis (*Prêt → En cours → Terminé / Arrêté*). Cette orchestration repose sur une logique de planification non bloquante via `root.after()`, garantissant la continuité de la boucle événementielle tout en maintenant une granularité de mise à jour stable (200 ms), assimilable à un **échantillonnage périodique** de l’état du protocole.

2. **Un module d’excitation motrice** (thread dédié) générant des perturbations spatio-temporelles du curseur par le biais d’un modèle stochastique simplifié. À chaque itération, la position instantanée ((x, y)) est acquise, puis un déplacement relatif ((\Delta x, \Delta y)) est tiré aléatoirement dans un intervalle borné ([-80, 80]), ce qui définit une nouvelle consigne ((x', y')). Cette consigne est ensuite **clampée** aux frontières de l’écran afin d’empêcher toute sortie du domaine ([0, W-1] \times [0, H-1]), ce qui garantit la **validité topologique** du mouvement sur la surface de rendu.

Le mouvement n’est pas instantané : il est réalisé via une interpolation temporelle de durée (d \in [0.15, 0.45]) secondes, modulée par une fonction de tweening de type **ease-in/ease-out** (profil d’accélération/décélération). Cette interpolation vise à réduire la discontinuité perceptive et à produire une trajectoire compatible avec un modèle cinématique à **vitesse non constante**, plus proche des signatures humaines que d’un saut discret. Un temps de repos (p \in [1.0, 3.0]) est ensuite appliqué entre deux excitations successives, introduisant un **jitter temporel** qui évite une périodicité trop régulière et permet de tester le système sous un régime d’entrée irrégulière.

Sur le plan de la synchronisation, le programme utilise un **signal d’arrêt asynchrone** (`threading.Event`) qui joue le rôle d’un mécanisme de terminaison coopérative. Le thread de mouvement vérifie explicitement ce signal avant et pendant ses phases d’attente, ce qui empêche les blocages prolongés et permet un arrêt réactif. La séparation thread UI / thread moteur est intentionnelle : elle assure que l’excitation motrice ne monopolise pas la boucle graphique, évitant une dégradation de l’interface (freeze) et maintenant une observabilité constante de l’état expérimental.

Enfin, le système intègre un **mécanisme de sécurité opérateur** : l’activation de `pyautogui.FAILSAFE` provoque une interruption immédiate si le pointeur atteint un coin de l’écran, interprétée comme un geste d’arrêt d’urgence. Cette interruption est capturée (`FailSafeException`) et se traduit par un passage contrôlé en état “Interrompu”, assurant la **robustesse** du protocole en cas de perte de contrôle perçue.

En résumé, l’outil met en œuvre une forme minimale de **génération de trajectoires stochastiques bornées**, temporisées et lissées, sous la supervision d’un ordonnanceur UI, afin de produire une séquence de mouvements exploitables pour l’observation des réactions d’un environnement graphique face à un périphérique de pointage piloté par script — autrement dit, une expérimentation très sérieuse… dont le résultat concret reste, avec une honnêteté brutale, “la souris bouge”.

## AVERTISSEMENT — USAGE STRICTEMENT LÉGITIME ET AUTORISÉ

Ce programme est un outil technique à finalité générale. Il n’est fourni **qu’à des fins de test, de démonstration, d’analyse et d’expérimentation** dans un cadre **légal**, **autorisé** et **conforme** aux règles applicables.

### Interdictions explicites

Il est **strictement interdit** d’utiliser ce programme, directement ou indirectement, pour :

* contourner ou violer des mécanismes d’anti-AFK, de présence, d’inactivité, de “keep-alive”, ou toute mesure de contrôle similaire ;
* enfreindre des conditions d’utilisation (ToS), chartes internes, règlements, politiques de sécurité, ou consignes d’un organisme/entreprise ;
* tromper un service, un système, un employeur, une plateforme, un jeu, un examen, ou tout dispositif de contrôle ;
* réaliser toute activité illégale, non autorisée, ou portant atteinte à autrui.

### Exigence d’autorisation

Vous ne devez utiliser ce programme **que** sur des systèmes dont vous êtes propriétaire ou pour lesquels vous disposez d’une **autorisation écrite explicite** du propriétaire / administrateur / responsable habilité.
En cas de doute : **n’utilisez pas ce programme**.

### Responsabilité de l’utilisateur

Vous reconnaissez être **seul responsable** :

* de vérifier la légalité de l’usage dans votre juridiction ;
* de vérifier la conformité aux conditions d’utilisation et règles applicables ;
* d’obtenir toutes autorisations nécessaires ;
* de tout impact, dommage, sanction, ou conséquence résultant de votre utilisation.

### Aucune garantie

Ce programme est fourni **“tel quel”**, sans aucune garantie, expresse ou implicite, incluant notamment (sans s’y limiter) les garanties de bon fonctionnement, d’adéquation à un usage particulier, d’absence d’erreurs, de sécurité, ou de compatibilité.

### Limitation maximale de responsabilité

Dans les limites autorisées par la loi, le créateur et les contributeurs ne pourront en aucun cas être tenus responsables de tout dommage direct ou indirect, y compris (sans limitation) pertes de données, pertes financières, sanctions disciplinaires, suspension de compte, interruption de service, dommages matériels, ou préjudices de toute nature, résultant de l’utilisation, de l’impossibilité d’utilisation, ou de la mauvaise utilisation du programme.

### Indemnisation

Vous acceptez d’indemniser et de dégager de toute responsabilité le créateur et les contributeurs contre toute réclamation, plainte, procédure, perte, coût, dommage ou dépense (y compris frais juridiques) découlant de votre utilisation du programme ou de toute violation des règles, lois, ou conditions d’utilisation.

### Acceptation

En utilisant, copiant, modifiant ou distribuant ce programme, vous confirmez avoir lu et accepté cet avertissement, et comprendre que **toute utilisation non autorisée est expressément exclue**.

## Installation (commandes a copier-coller)
```bash
python -m pip install -r requirements.txt
```

Tkinter est inclus avec la plupart des distributions Python standard. PyAutoGUI est installe via `requirements.txt`.

## Utilisation
```bash
python LikeToMoveIt.py
```

Choisissez la durée en minutes, cliquez sur Démarrer, puis le pointeur se déplace légèrement de manière aléatoire tant que le minuteur tourne. Cliquez sur Arrêt ou mettez le pointeur dans le coin supérieur gauche (fail-safe PyAutoGUI) pour interrompre.

## À faire pour débloquer l'accès au display (si erreur DISPLAY/Xauthority)
- Ouvrez un terminal dans votre session graphique (pas sudo) et vérifiez `echo $DISPLAY` -> `:0` (ou similaire).
- Autorisez l'utilisateur courant à accéder au display : `xhost +SI:localuser:$(whoami)`.
