\# 📖 Actions API SENTRA\_CORE\_MEM – Résumé et Prompts



\## 🔗 \*\*Endpoints disponibles\*\*



| Méthode | Endpoint      | Description                                      | Exemples de prompt naturel                                 |

|---------|--------------|--------------------------------------------------|------------------------------------------------------------|

| GET     | `/memoire`   | Liste toutes les entrées mémoire                 | « Montre la mémoire »<br>« Liste toutes les notes »        |

| POST    | `/memoire`   | Ajoute une nouvelle entrée mémoire               | « Ajoute la note : ... »<br>« Enregistre : ... »           |

| GET     | `/logs`      | Récupère tous les logs                           | « Quels sont les derniers logs ? »                         |

| POST    | `/backup`    | Sauvegarde la mémoire                            | « Fais une sauvegarde »<br>« Crée un backup mémoire »      |

| POST    | `/restore`   | Restaure depuis un backup                        | « Restaure la mémoire depuis le backup X »                 |

| POST    | `/glyph`     | Traduit du texte en glyphes                      | « Traduis ce texte en glyphes : ... »                      |

| GET     | `/readme`    | Récupère le README du projet                     | « Affiche le README »                                      |

| GET     | `/status`    | Donne le statut de l’API                         | « Quel est le statut de l’API ? »                          |

| GET     | `/version`   | Renvoie la version de l’API                      | « Quelle version du noyau ? »                              |



---



\## 📝 \*\*Prompts naturels recommandés\*\*



\- \*\*Ajouter une note\*\* :  

&nbsp; > Ajoute une note : “Tester la sauvegarde de la mémoire.”



\- \*\*Lire la mémoire\*\* :  

&nbsp; > Montre-moi toutes les notes de mémoire.



\- \*\*Lire les logs\*\* :  

&nbsp; > Affiche les derniers logs.



\- \*\*Faire une sauvegarde\*\* :  

&nbsp; > Sauvegarde la mémoire.



\- \*\*Restaurer une sauvegarde\*\* :  

&nbsp; > Restaure la mémoire depuis le backup numéro 2.



\- \*\*Traduction glyphique\*\* :  

&nbsp; > Traduis ce texte en glyphes : ‘Mémoire IA persistante’



\- \*\*Afficher le README\*\* :  

&nbsp; > Montre-moi le README du projet.



\- \*\*Vérifier l’API\*\* :  

&nbsp; > API status ?



\- \*\*Version\*\* :  

&nbsp; > Quelle version de SENTRA\_CORE\_MEM est installée ?



---



> \*\*À chaque appel, vérifie la console FastAPI pour voir passer la requête (ex : “POST /memoire HTTP/1.1” 200 OK) et garantir le passage par l’API.\*\*



---



\*\*Tu peux copier-coller ce bloc tel quel dans ton README, Notice utilisateur ou pour onboarder un nouvel agent !\*\*



