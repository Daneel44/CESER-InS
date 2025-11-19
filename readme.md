# CESER-InS
Projet Hackaton pour le CESER

Pour lancer le projet :
`docker build -t flask-simple .`
Puis lancer le container en remplaçant par votre clé openAPI
`docker run --rm -e OPENAI_API_KEY=sk-... PORT=5000 -p 5000:5000 flask-app `

Sur le site http://127.0.0.1:5000/
Vous pouvez uploader un fichier de décisions du conseil régional. 