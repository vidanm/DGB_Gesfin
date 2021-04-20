from .revenues import Revenues
from .categories import Categories
from .imports import get_csv_expenses
from .expenses import Expenses
import pandas as pd
import datetime
import os


class Office(Categories):
    def __init__(self,
                 accounting_plan,
                 month,
                 year,
                 csv_path="var/csv/"):
        """Trie les expenses de la structure par postes."""
        super(Office, self).__init__(accounting_plan.get_office_plan())
        self.csv_path = csv_path
        self.row_names = [1]
        self.year = year
        self.month = month
        print("ALLO\n")
        self.expenses = self.__get_year_data_of_office(accounting_plan)
        print("OLLA\n\n\n")
        print("ALLO\n")
        self.year_expenses = self.__get_year_expenses(accounting_plan)
        print("OLLA\n\n\n")
        if self.expenses is None:
            raise ValueError("Pas de dépenses pour la structure pour ce mois")

        for name in self.category_names:
            self.categories[name]['%CA MOIS'] = 0
            self.categories[name]['%CA Cumul'] = 0

    def __get_year_data_of_office(self, accounting_plan):
        total = None
        for filename in os.listdir(self.csv_path):
            if "STRUCT" in filename and str(
                    self.year) in filename and filename.endswith(".csv"):
                if total is None:
                    total = Expenses(
                        get_csv_expenses(self.csv_path + filename),
                        accounting_plan)
                else:
                    total += Expenses(
                        get_csv_expenses(self.csv_path + filename),
                        accounting_plan)
        if total is None:
            raise ValueError("Aucune dépense\
                    liée à la structure dans le fichier de charges")
        else:
            return total

    def __get_year_expenses(self, accounting_plan):
        total = None
        for filename in os.listdir(self.csv_path):
            print(str(self.year) + " : " + filename)
            if str(self.year) in filename and filename.endswith(".csv"):
                if total is None:
                    total = Expenses(
                            get_csv_expenses(self.csv_path + filename),
                            accounting_plan, with_category=False)
                else:
                    total += Expenses(
                            get_csv_expenses(self.csv_path + filename),
                            accounting_plan, with_category=False)

        if total is None:
            raise ValueError("Aucune charges importées")
        else:
            return total

    def calculate_office(self):
        month = int(self.month)
        for _, row in self.expenses.data.iterrows():
            date = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
            if (row['POSTE'] in self.category_names):
                if (date.month <= month and date.year == self.year):
                    super(Office, self)._add_cumulative_expense(row)
                    if (date.month == month):
                        super(Office, self)._add_month_expense(row)
        self._add_revenues(month, self.year)
        self.add_office_total()

    def format_for_pdf(self):
        self.row_names = [
            1
        ]  # On garde les positions des names de poste pour
        # pouvoir les colorier différemment
        for name in self.category_names:
            if (self.category_names.index(name) == 0):
                title = pd.DataFrame([[]], [name])
                formatted_office = pd.DataFrame(self.categories[name])
                formatted_office = title.append(formatted_office)
            else:
                self.row_names.append(len(formatted_office) + 1)
                title = pd.DataFrame([[]], [name])
                formatted_office = formatted_office.append(title)
                formatted_office = formatted_office.append(
                    self.categories[name])

        return formatted_office

    def _add_revenues(self, month, year):
        revenues = Revenues(self.year_expenses.data)
        month_revenue = revenues.calculate_month_revenues(month, year)
        year_revenue = revenues.calculate_year_revenues(year)
        for name in self.category_names:
            for _, row in self.categories[name].iterrows():
                month_expenses = self.categories[name].loc[row.name,
                                                           'Dépenses du mois']
                cumulative_expenses = self.categories[name].loc[
                    row.name, "Dépenses cumulées"]
                self.categories[name].loc[
                    row.name,
                    '%CA MOIS'] = month_expenses * 100 / month_revenue
                self.categories[name].loc[
                    row.name,
                    '%CA Cumul'] = cumulative_expenses * 100 / year_revenue

    def add_category_total(self):
        month_total = 0
        year_total = 0
        month_revenues = 0
        year_revenues = 0

        for name in self.category_names:
            for index, row in self.categories[name].iterrows():
                month_total += self.categories[name].loc[row.name,
                                                         "Dépenses du mois"]
                year_total += self.categories[name].loc[row.name,
                                                        "Dépenses cumulées"]
                month_revenues += self.categories[name].loc[row.name,
                                                            "%CA MOIS"]
                year_revenues += self.categories[name].loc[row.name,
                                                           "%CA Cumul"]

        total = pd.DataFrame(
            {
                "Dépenses du mois": [month_total],
                "Dépenses cumulées": [year_total],
                "%CA MOIS": [month_revenues],
                "%CA Cumul": [year_revenues]
            }, ["TOTAL"])

        self.categories[name] = self.categories[name].append(total)

    def add_office_total(self):
        self.add_category_total()
