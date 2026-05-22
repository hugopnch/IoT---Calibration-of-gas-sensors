from tkinter import Tk
from block1_1 import Block1Read
from block2_1 import Block2Analysis
from block3main import Block3Main
from block4main import Block4Main

if __name__ == "__main__":
    root = Tk()
    root.title("Gas data analysis")

    # Configuration des colonnes et lignes de la fenêtre principale
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)

    # Création du Bloc 4 (mais il ne sera pas visible tant que les données ne sont pas reçues)
    bloc4 = Block4Main(root)

    # Création du Bloc 3 (avec callback pour le Bloc 4)
    bloc3 = Block3Main(root, callback_on_update=bloc4.update_from_block3)
    bloc3.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

    # Création du Bloc 2 (avec callback pour le Bloc 3)
    bloc2 = Block2Analysis(root, dataframes={}, callback_on_update=bloc3.update_from_block2, callback_on_update_bis = bloc4.update_from_bloc2)
    bloc2.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    # Création du Bloc 1 (avec callback pour le Bloc 2)
    bloc1 = Block1Read(root, callback_on_load=bloc2.update_from_block1)
    bloc1.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

    root.mainloop()

