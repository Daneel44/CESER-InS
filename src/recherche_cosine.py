from typing import Any
from src.embedding.embedding import EmbeddingModel
import pandas as pd
import numpy as np
import os


class RechercheCosine:
    def __init__(self) -> None:
        self.model = EmbeddingModel()
        self.preconisations = pd.read_excel("sources/preconisations_CESER.xlsx")
        self.liste_preco_str = self.liste_preco(self.preconisations)
        if self.verifier_vecteurs():
            self.vecteur_preco = np.load("vecteurs_preconisation.npy")
        else:
            self.vecteur_preco = self.vectorize_preco(self.liste_preco_str)

    def verifier_vecteurs(self) -> bool:
        filename = "vecteurs_preconisation.npy"

        # Vérifier si le fichier existe
        if os.path.exists(filename):
            return True
        else:
            return False

    def vectorize_preco(self, liste_preco_str):
        vecteurs = []
        print("vectorizing")
        for preco in liste_preco_str:
            print(preco)
            v = self.model.embed_query(preco)
            print(v)
            vecteurs.append(v)
        vecteurs = np.array(vecteurs)
        np.save("vecteurs_preconisation.npy", vecteurs)
        return vecteurs

    def colonnes_preco(
        self, dataframe
    ) -> tuple[list[Any], list[Any], list[Any], list[Any], list[Any]]:
        themes_preco = [exemple for exemple in dataframe.get("Thème")]
        sous_themes_preco = [exemple for exemple in dataframe.get("Sous-Thème")]
        constats_preco = [exemple for exemple in dataframe.get("Constat")]
        titres_preco = [exemple for exemple in dataframe.get("Titre préconisation")]
        desc_preoc = [exemple for exemple in dataframe.get("Détail")]
        return themes_preco, sous_themes_preco, constats_preco, titres_preco, desc_preoc

    def liste_preco(self, dataframe):
        exemples_preco = [exemple for exemple in dataframe.get("Titre préconisation")]
        detail_preco = [exemple for exemple in dataframe.get("Détail")]
        liste_preco = []
        i = 0
        for preco in exemples_preco:
            texte_preco = f"""{preco} : {detail_preco[i]}"""
            liste_preco.append(texte_preco)
            i += 1
        return liste_preco

    def get_file_to_search(self) -> list[str]:
        return [
            "En particulier les fermes expérimentales qui permettent d’impulser des programmes de R&D et de conduire des programmes de recherche appliquée dans des conditions réelles et donc transférables. Le CESER invite la Région à accompagner leur essor et leur plein déploiement sur l’ensemble du territoire régional.Dans ce cadre, améliorer les connaissances sur les effets des pesticides sur la santé des consommateurs et des producteurs, ceux de la consommation de produits transformés sur la santé... ainsi que sur les conséquences du changement climatique (évolution des espèces, associations de plantes, prévention et lutte contre nouveaux parasites, maladies ...)."
        ]

    def creer_vecteurs_decisions(
        self, liste_texte: list[str], titre_document: str
    ):
        vecteurs = []
        filename = f"vecteurs_{titre_document}_.npy"

        # Vérifier si le fichier existe
        if os.path.exists("src/vecteurs_decision/" + filename):
            return np.load("src/vecteurs_decision/" + filename)
        else:
            for text in liste_texte:
                vecteurs.append(self.model.embed_query(text))
            vecteurs = np.array(vecteurs)
            np.save("src/vecteurs_decision/" + filename, vecteurs)
            return vecteurs

    def trouver_cosine_pour_preconisations(
        self, vecteurs_decisions, list_decision:list[str],date:str
    ) -> dict[str, list[Any]]:
        print(vecteurs_decisions)
        print(list_decision)
        list_final = {
            "Thème": [],
            "Sous-Thème": [],
            "Constat": [],
            "Titre préconisation": [],
            "Détail préconisation": [],
            "Date de la décision": [],
            "Titre décision": [],
            "Détail décision": [],
            "Coefficient de similarité": [],
        }
        theme_list: list[str] = []
        sous_theme_list: list[str] = []
        constat_list: list[str] = []
        titre_preco_list: list[str] = []
        detail_preco_list: list[str] = []
        date_list: list[str] = []
        titre_decision_list: list[str] = []
        detail_decision_list: list[str] = []
        coef_list: list[float] = []

        themes_preco, sous_themes_preco, constats_preco, titres_preco, desc_preoc = (
            self.colonnes_preco(self.preconisations)
        )
        print('ok')
        preco_vecteurs = self.vecteur_preco
        
        
        i = 0
        for titre in titres_preco:
            theme = themes_preco[i]
            sous_theme = sous_themes_preco[i]
            constat = constats_preco[i]
            detail = desc_preoc[i]
            vecteur_preco = preco_vecteurs[i]
            f = 0
            # for titre_decision in titres_delib:
            #     description = descriptions_delib[f]
            #     date_decision = dates_delib[f]
            #     vecteur_decision = vecteurs_decision[f]
            #     cosine_distance = EmbeddingModel().cosine_distance(
            #         np.array(vecteur_preco), np.array(vecteur_decision)
            #     )
            for decision in list_decision:
                theme_list.append(theme)
                sous_theme_list.append(sous_theme)
                constat_list.append(constat)
                titre_preco_list.append(titre)
                detail_preco_list.append(detail)
                date_list.append(date)
                titre_decision_list.append("")
                detail_decision_list.append(decision)
                coef_list.append(EmbeddingModel().cosine_distance(vecteur_preco, vecteurs_decisions[f]))
                f += 1
            i += 1

        list_final["Thème"] = theme_list
        list_final["Sous-Thème"] = sous_theme_list
        list_final["Constat"] = constat_list
        list_final["Titre préconisation"] = titre_preco_list
        list_final["Détail préconisation"] = detail_preco_list
        list_final["Date de la décision"] = date_list
        list_final["Titre décision"] = titre_decision_list
        list_final["Détail décision"] = detail_decision_list
        list_final["Coefficient de similarité"] = coef_list
        return list_final

    def result_to_csv(self, liste_finale: dict[str, list[Any]]) -> None:
        final = pd.DataFrame.from_dict(liste_finale)
        print(final.head())
        df_sorted = final.sort_values(by="Coefficient de similarité", ascending=False)
        df_sorted.to_csv("final.csv")

    def result_to_exel(self, liste_finale: dict[str, list[Any]], titre_document):
        final = pd.DataFrame.from_dict(liste_finale)
        df_sorted = final.sort_values(by="Coefficient de similarité", ascending=False)
        df_sorted.to_excel(
            "src/finals/"+titre_document+".xlsx",
            columns=[
                "Thème",
                "Sous-Thème",
                "Constat",
                "Titre préconisation",
                "Détail préconisation",
                "Date de la décision",
                "Titre décision",
                "Détail décision",
                "Coefficient de similarité",
            ],
        )